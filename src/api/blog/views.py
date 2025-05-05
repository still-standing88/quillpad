# api/blog/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import Post, Comment, Category, PostLike, SavedPost
from rest_framework.response import Response
from .serializers import PostSerializer, CommentSerializer, CategorySerializer, TagSerializer
from taggit.models import Tag
from taggit.serializers import TaggitSerializer
from django_filters import rest_framework as filters
from .pagination import StandardResultsSetPagination, PostLimitOffsetPagination
# --- Add logging ---
import logging
logger = logging.getLogger(__name__)
# --- End logging import ---
# --- Add Permission Denied ---
from rest_framework.exceptions import PermissionDenied
# --- End Add Permission Denied ---


# --- Permissions with Logging ---
# (Copy the updated IsAdminEditorOrReadOnly and IsAuthorEditorAdminOrReadOnly
#  classes with logging from api/users/views.py modification above)

class IsAdminEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        role = getattr(user, 'role', 'N/A')
        logger.debug(f"[PermCheck:IsAdminEditorOrReadOnly:has_permission] User: {user}, Role: {role}, Staff: {user.is_staff}, Method: {request.method}, View: {view.__class__.__name__}")
        if request.method in permissions.SAFE_METHODS:
            return True
        is_auth = user.is_authenticated
        has_role = is_auth and (user.is_staff or role in ['admin', 'editor'])
        logger.debug(f"[PermCheck:IsAdminEditorOrReadOnly:has_permission] IsAuth: {is_auth}, HasRole: {has_role}. Granting: {has_role}")
        return has_role

class IsAuthorEditorAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, 'role', 'N/A')
        obj_type = type(obj).__name__
        logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] User: {user}, Role: {role}, Staff: {user.is_staff}, Method: {request.method}, ObjType: {obj_type}, View: {view.__class__.__name__}")
        if request.method in permissions.SAFE_METHODS:
            logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] Safe method. Granting.")
            return True

        if not user.is_authenticated:
            logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] User not authenticated. Denying.")
            return False

        is_admin_or_editor = user.is_staff or role in ['admin', 'editor']
        is_author = False
        obj_author = getattr(obj, 'author', None)
        if obj_author:
             is_author = (obj_author == user)
             logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] Object author: {obj_author}, IsAuthor check: {is_author}")

        grant = is_author or is_admin_or_editor
        logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] IsAuthor: {is_author}, IsAdmin/Editor: {is_admin_or_editor}. Granting: {grant}")
        return grant

# --- End Permissions with Logging ---


class PostFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name')
    author = filters.CharFilter(field_name='author__username')
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['category', 'author', 'tags', 'is_published', 'featured']


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    # Use the logged permission classes
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorEditorAdminOrReadOnly]
    pagination_class = PostLimitOffsetPagination
    filterset_fields = ['category', 'author__username']
    filterset_class = PostFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Explicit check remains as a safeguard
        user = self.request.user
        role = getattr(user, 'role', 'reader')
        is_staff = getattr(user, 'is_staff', False)
        allowed_roles = ['admin', 'editor', 'author']

        logger.info(f"Backend Create Post: User '{user.username}' (Role: {role}, Staff: {is_staff}) attempting creation. Data: {serializer.validated_data}")

        if not (user.is_authenticated and (role in allowed_roles or is_staff)):
             logger.error(f"Backend Create Post: Permission DENIED for user '{user.username}' with role '{role}'.")
             raise PermissionDenied("You do not have permission to create posts.")

        logger.info(f"Backend Create Post: Permission GRANTED. Saving post for author '{user.username}'.")
        serializer.save(author=user)


    # --- Add logging to other relevant actions ---
    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        logger.info(f"Backend Update Post: User '{user.username}' attempting update for post '{instance.slug}'. Data: {serializer.validated_data}")
        serializer.save()
        logger.info(f"Backend Update Post: Post '{instance.slug}' updated successfully.")

    def perform_destroy(self, instance):
        user = self.request.user
        logger.warning(f"Backend Delete Post: User '{user.username}' attempting deletion of post '{instance.slug}'.")
        instance.delete()
        logger.warning(f"Backend Delete Post: Post '{instance.slug}' deleted successfully.")

    # --- Keep other actions (@action methods) as they were ---
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        # ... (no changes needed here, permissions handled by viewset) ...
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def view(self, request, slug=None):
        # ... (no changes needed here) ...
        post = self.get_object()
        post.increment_view()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        # ... (no changes needed here) ...
         featured_posts = Post.objects.filter(featured=True, is_published=True)
         serializer = self.get_serializer(featured_posts, many=True)
         return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        # ... (no changes needed here) ...
        post = self.get_object(); user = request.user
        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if not created: like.delete(); return Response({'status': 'unliked', 'liked': False, 'like_count': post.likes.count()})
        return Response({'status': 'liked', 'liked': True, 'like_count': post.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save(self, request, slug=None):
        # ... (no changes needed here) ...
        post = self.get_object(); user = request.user
        saved, created = SavedPost.objects.get_or_create(user=user, post=post)
        if not created: saved.delete(); return Response({'status': 'unsaved', 'saved': False})
        return Response({'status': 'saved', 'saved': True})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def saved(self, request):
        # ... (no changes needed here) ...
        saved_posts = Post.objects.filter(saved_by__user=request.user).order_by('-saved_by__created_at')
        page = self.paginate_queryset(saved_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(saved_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        # ... (no changes needed here) ...
        return Response({'total_posts': Post.objects.count(), 'published_posts': Post.objects.filter(is_published=True).count(), 'total_comments': Comment.objects.count(), 'total_categories': Category.objects.count(), 'total_tags': Tag.objects.count()})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        # ... (no changes needed here) ...
        count = int(request.query_params.get('count', 5))
        posts = self.get_queryset()[:count]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        # ... (no changes needed here) ...
        username = request.query_params.get('username', None)
        if not username: return Response({"error": "Username parameter is required"}, status=400)
        posts = self.get_queryset().filter(author__username=username)
        page = self.paginate_queryset(posts)
        if page is not None: serializer = self.get_serializer(page, many=True); return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True); return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        # ... (no changes needed here) ...
        category_slug = request.query_params.get('slug', None)
        if not category_slug: return Response({"error": "Category slug parameter is required"}, status=400)
        posts = self.get_queryset().filter(category__slug=category_slug)
        page = self.paginate_queryset(posts);
        if page is not None: serializer = self.get_serializer(page, many=True); return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True); return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        # ... (no changes needed here) ...
        tag_name = request.query_params.get('name', None)
        if not tag_name: return Response({"error": "Tag name parameter is required"}, status=400)
        posts = self.get_queryset().filter(tags__name=tag_name)
        page = self.paginate_queryset(posts)
        if page is not None: serializer = self.get_serializer(page, many=True); return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True); return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, slug=None):
         # ... (no changes needed here) ...
         post = self.get_object(); data = {'id': post.id, 'title': post.title, 'slug': post.slug, 'author': post.author.username, 'created_at': post.created_at, 'updated_at': post.updated_at, 'category': post.category.name if post.category else None, 'tags': [tag.name for tag in post.tags.all()], 'comment_count': post.comments.count(), 'view_count': post.view_count, 'featured_image_url': self.get_serializer(post).data.get('featured_image_url') }; return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminEditorOrReadOnly] # Use logged version

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorEditorAdminOrReadOnly] # Use logged version

    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"Backend Create Comment: User '{user.username}' creating comment. Data: {serializer.validated_data}")
        serializer.save(author=user)
        logger.info(f"Backend Create Comment: Comment saved successfully for user '{user.username}'.")

    @action(detail=False, methods=['get'])
    def by_post(self, request):
         # ... (no changes needed here) ...
         post_id = request.query_params.get('post_id', None)
         if post_id:
             comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
             page = self.paginate_queryset(comments)
             if page is not None: serializer = self.get_serializer(page, many=True); return self.get_paginated_response(serializer.data)
             serializer = self.get_serializer(comments, many=True); return Response(serializer.data)
         return Response({"error": "post_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        # ... (no changes needed here) ...
        tag = self.get_object(); posts_queryset = Post.objects.filter(tags__name__in=[tag.name], is_published=True).order_by('-created_at')
        paginator = PostLimitOffsetPagination(); page = paginator.paginate_queryset(posts_queryset, request, view=self)
        if page is not None: serializer = PostSerializer(page, many=True, context={'request': request}); return paginator.get_paginated_response(serializer.data)
        serializer = PostSerializer(posts_queryset, many=True, context={'request': request}); return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        # ... (no changes needed here) ...
        from django.db.models import Count
        tags = Tag.objects.annotate(post_count=Count('taggit_taggeditem_items')).order_by('-post_count')[:10]
        serializer = self.get_serializer(tags, many=True); return Response(serializer.data)