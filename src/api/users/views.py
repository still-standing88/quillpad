from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from blog.models import Post, Comment
from .serializers import RegisterSerializer, UserSerializer, ActivitySerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'username': token.user.username
        })

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class IsAdminEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_editor_or_admin

class IsAuthorEditorAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'author'):
            return (obj.author == request.user or 
                    request.user.is_editor_or_admin)
        return request.user.is_editor_or_admin

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        if not user.check_password(request.data.get('current_password', '')):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_password = request.data.get('new_password', '')
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'error': list(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        return Response({'message': 'Password updated successfully'})

class UserActivityView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        posts = Post.objects.filter(author=user)
        comments = Comment.objects.filter(author=user)
        
        activities = []
        for post in posts:
            activities.append({
                'type': 'post',
                'object': post,
                'created_at': post.created_at
            })
        for comment in comments:
            activities.append({
                'type': 'comment',
                'object': comment,
                'created_at': comment.created_at
            })        
        return sorted(activities, key=lambda x: x['created_at'], reverse=True)
