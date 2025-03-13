from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action

from .models import Post, Comment, Category, PostLike, SavedPost
from rest_framework.response import Response
from .serializers import PostSerializer, CommentSerializer, CategorySerializer, TagSerializer
from taggit.models import Tag
from taggit.serializers import TaggitSerializer
from django_filters import rest_framework as filters
from .pagination import StandardResultsSetPagination, PostLimitOffsetPagination


class IsAdminEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or 
            getattr(request.user, 'role', '') in ['admin', 'editor']
        )

class IsAuthorEditorAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if not request.user.is_authenticated:
            return False
        is_admin_or_editor = (
            request.user.is_staff or 
            getattr(request.user, 'role', '') in ['admin', 'editor']
        )
        is_author = hasattr(obj, 'author') and obj.author == request.user        
        return is_author or is_admin_or_editor

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorEditorAdminOrReadOnly]
    pagination_class = PostLimitOffsetPagination
    filterset_fields = ['category', 'author__username']
    filterset_class = PostFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    ordering = ['-created_at']
    lookup_field = 'slug' # <--- ADD THIS LINE

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

# src/api/blog/views.py (Inside PostViewSet)
# ADD permission_classes=[permissions.AllowAny] to the @action decorator

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def view(self, request, slug=None):
        post = self.get_object()
        post.increment_view()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = Post.objects.filter(featured=True, is_published=True)
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        post = self.get_object()
        user = request.user

        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'liked': False, 'like_count': post.likes.count()}) # Provide updated state
        return Response({'status': 'liked', 'liked': True, 'like_count': post.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated]) # Added permission
    def save(self, request, slug=None):
        post = self.get_object()
        user = request.user

        saved, created = SavedPost.objects.get_or_create(user=user, post=post)
        if not created:
            saved.delete()
            return Response({'status': 'unsaved', 'saved': False}) # Provide updated state
        return Response({'status': 'saved', 'saved': True}) # Provide updated state

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated]) # Added permission
    def saved(self, request):
        # Ensure pagination works correctly if needed
        saved_posts = Post.objects.filter(saved_by__user=request.user).order_by('-saved_by__created_at')
        page = self.paginate_queryset(saved_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(saved_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response({
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(is_published=True).count(),
            'total_comments': Comment.objects.count(),
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent posts with optional count parameter"""
        count = int(request.query_params.get('count', 5))
        posts = self.get_queryset()[:count]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get posts by specific user"""
        username = request.query_params.get('username', None)
        if not username:
            return Response({"error": "Username parameter is required"}, status=400)
            
        posts = self.get_queryset().filter(author__username=username)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get posts by category slug"""
        category_slug = request.query_params.get('slug', None)
        if not category_slug:
            return Response({"error": "Category slug parameter is required"}, status=400)
            
        posts = self.get_queryset().filter(category__slug=category_slug)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """Get posts by tag name"""
        tag_name = request.query_params.get('name', None)
        if not tag_name:
            return Response({"error": "Tag name parameter is required"}, status=400)
            
        posts = self.get_queryset().filter(tags__name=tag_name)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, slug=None):
        post = self.get_object()

        data = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'author': post.author.username,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'category': post.category.name if post.category else None,
            'tags': [tag.name for tag in post.tags.all()],
            'comment_count': post.comments.count(),
            'view_count': post.view_count, # Add view count
            'featured_image_url': self.get_serializer(post).data.get('featured_image_url') 
        }
        return Response(data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminEditorOrReadOnly]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorEditorAdminOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_post(self, request):
        post_id = request.query_params.get('post_id', None)
        if post_id:
            comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data)
        return Response({"error": "post_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts_queryset = Post.objects.filter(tags__name__in=[tag.name], is_published=True).order_by('-created_at')

        paginator = PostLimitOffsetPagination() # Or StandardResultsSetPagination
        page = paginator.paginate_queryset(posts_queryset, request, view=self)

        if page is not None:
             # context= {'request'
            serializer = PostSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts_queryset, many=True, context={'request': request})
        return Response(serializer.data)        

    @action(detail=False, methods=['get'])
    def popular(self, request):
        # Get tags ordered by number of posts
        from django.db.models import Count
        tags = Tag.objects.annotate(post_count=Count('taggit_taggeditem_items')).order_by('-post_count')[:10]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)