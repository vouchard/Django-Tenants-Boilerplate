"""
URL patterns for user management and authentication.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserListCreateView,
    UserDetailView,
    CurrentUserView,
    ChangePasswordView
)

app_name = 'users'

urlpatterns = [
    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Management
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
