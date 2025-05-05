# api/users/views.py
from rest_framework import generics, permissions, status, mixins # Ensure mixins is imported
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError, PermissionDenied # Import PermissionDenied
from django.shortcuts import get_object_or_404
from blog.models import Post, Comment
from .serializers import RegisterSerializer, UserSerializer, ActivitySerializer, AdminUserUpdateSerializer
from rest_framework.permissions import IsAdminUser
from blog.pagination import PostLimitOffsetPagination
# --- Add logging ---
import logging
logger = logging.getLogger(__name__)
# --- End logging import ---
# --- Add cache import (optional, for explicit clearing) ---
# from django.core.cache import cache
# --- End cache import ---


User = get_user_model()

# --- Permissions with Logging ---
class IsAdminEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        role = getattr(user, 'role', 'N/A')
        logger.debug(f"[PermCheck:IsAdminEditorOrReadOnly:has_permission] User: {user}, Role: {role}, Staff: {user.is_staff}, Method: {request.method}")
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
        logger.debug(f"[PermCheck:IsAuthorEditorAdminOrReadOnly:has_object_permission] User: {user}, Role: {role}, Staff: {user.is_staff}, Method: {request.method}, ObjType: {obj_type}")
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

# Add logging to Django's IsAdminUser for clarity
class LoggedIsAdminUser(IsAdminUser):
     def has_permission(self, request, view):
         user = request.user
         role = getattr(user, 'role', 'N/A')
         is_staff = getattr(user, 'is_staff', False)
         is_active = getattr(user, 'is_active', False)
         logger.debug(f"[PermCheck:IsAdminUser:has_permission] User: {user}, Role: {role}, Staff: {is_staff}, Active: {is_active}")
         allow = super().has_permission(request, view)
         logger.debug(f"[PermCheck:IsAdminUser:has_permission] Granting: {allow}")
         return allow

# --- End Permissions with Logging ---


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
             serializer.is_valid(raise_exception=True)
        except Exception as e:
             logger.error(f"Login validation failed: {e}, Data: {request.data}")
             raise # Re-raise the exception for DRF to handle
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        try:
            # Explicitly re-fetch user state from DB
            current_user_state = get_object_or_404(User, pk=user.pk)
            logger.info(f"Backend Login: Successfully validated '{user.username}'. Re-fetched state, role is '{current_user_state.role}'.")
        except Exception as e:
             logger.error(f"Backend Login: Failed to re-fetch user state for '{user.username}' after validation: {e}")
             current_user_state = user # Fallback

        return Response({
            'token': token.key,
            'user_id': current_user_state.id,
            'username': current_user_state.username,
            'role': current_user_state.role # Use potentially fresher role
        })

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [LoggedIsAdminUser] # Use logged version
    pagination_class = PostLimitOffsetPagination

class UserDetailView(generics.RetrieveUpdateDestroyAPIView): # KEEP THIS CHANGE
    queryset = User.objects.all()
    permission_classes = [LoggedIsAdminUser] # Use logged version

    def get_serializer_class(self):
        # Use AdminUserUpdateSerializer for PUT/PATCH, otherwise UserSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUserUpdateSerializer
        return UserSerializer

    # --- MODIFIED: Add logging and potential cache clearing to update ---
    def perform_update(self, serializer):
        instance = serializer.instance
        original_role = getattr(instance, 'role', 'N/A')
        logger.info(f"Backend Update User: Attempting update for user '{instance.username}' (ID: {instance.pk}). Original role: {original_role}. Data: {serializer.validated_data}")

        # Save the instance
        updated_instance = serializer.save()

        # Log the state immediately after save
        # Fetch again to be absolutely sure what's in the DB
        try:
            saved_state = User.objects.get(pk=updated_instance.pk)
            new_role = getattr(saved_state, 'role', 'N/A')
            logger.info(f"Backend Update User: User '{saved_state.username}' saved. Role in DB is now: {new_role}")

            # --- Optional: Explicit Cache Clearing ---
            # If you suspect caching is involved, uncomment and adapt cache key logic
            # cache_key = f'user_data_{saved_state.pk}'
            # cache.delete(cache_key)
            # logger.info(f"Backend Update User: Attempted to clear cache key '{cache_key}'.")
            # --- End Optional Cache Clearing ---

        except User.DoesNotExist:
             logger.error(f"Backend Update User: CRITICAL! User '{updated_instance.username}' not found immediately after save!")
        except Exception as e:
             logger.error(f"Backend Update User: Error fetching/clearing cache after save for '{updated_instance.username}': {e}")


    def perform_destroy(self, instance):
        logger.warning(f"Backend Delete User: Admin '{self.request.user}' attempting deletion of user '{instance.username}' (ID: {instance.pk}).")
        if instance == self.request.user:
            logger.error(f"Backend Delete User: Admin '{self.request.user}' attempted self-deletion. Denied.")
            raise PermissionDenied("Administrators cannot delete their own account.")
        instance.delete()
        logger.warning(f"Backend Delete User: User '{instance.username}' deleted successfully.")

# --- End UserDetailView Modification ---


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Standard check is fine here

    def get_object(self):
        # Log which user's profile is being fetched by the authenticated request
        user = self.request.user
        logger.debug(f"Backend Get Profile: Fetching profile for authenticated user '{user.username}' (Role: {getattr(user, 'role', 'N/A')})")
        return user

    # Optional: Add logging to profile update as well
    def perform_update(self, serializer):
        instance = serializer.instance
        logger.info(f"Backend Update Profile: User '{instance.username}' updating profile. Data: {serializer.validated_data}")
        serializer.save()
        logger.info(f"Backend Update Profile: Profile for '{instance.username}' saved.")


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        logger.info(f"Backend Change Password: User '{user.username}' attempting password change.")
        if not user.check_password(request.data.get('current_password', '')):
            logger.warning(f"Backend Change Password: Incorrect current password for user '{user.username}'.")
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password', '')
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            logger.warning(f"Backend Change Password: New password validation failed for user '{user.username}': {list(e.messages)}")
            return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        # Invalidate old tokens
        Token.objects.filter(user=user).delete()
        # Optionally issue a new one if needed immediately, but usually requires re-login
        # new_token = Token.objects.create(user=user)
        logger.info(f"Backend Change Password: Password changed successfully for user '{user.username}'. Old tokens invalidated.")
        return Response({'message': 'Password updated successfully. Please log in again.'}, status=status.HTTP_200_OK)


class UserActivityView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Optimized slightly: select related author to avoid extra queries if serializers need it
        posts = Post.objects.filter(author=user).select_related('author')
        comments = Comment.objects.filter(author=user).select_related('author')

        activities = []
        for post in posts: activities.append({'type': 'post', 'object': post, 'created_at': post.created_at})
        for comment in comments: activities.append({'type': 'comment', 'object': comment, 'created_at': comment.created_at})

        return sorted(activities, key=lambda x: x['created_at'], reverse=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context