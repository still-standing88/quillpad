from django.urls import path
from .views import (
    RegisterView, CustomAuthToken, UserListView, UserProfileView,
    ChangePasswordView, UserActivityView,
    UserDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('activity/', UserActivityView.as_view(), name='user-activity'),
]