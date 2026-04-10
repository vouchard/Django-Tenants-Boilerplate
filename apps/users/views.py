"""
Views for user management within tenants.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user in the current tenant.
    Only admin users can access this endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(
        summary="List all users",
        description="Get all users in the current tenant (Admin only)",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new user",
        description="Create a new user in the current tenant (Admin only)",
        request=UserCreateSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user.
    Only admin users can access this endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        summary="Get current user profile",
        description="Retrieve the authenticated user's information",
        responses={200: UserSerializer}
    )
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Change password",
        description="Change the password for the authenticated user",
        request=ChangePasswordSerializer,
        responses={200: {"message": "Password updated successfully"}}
    )
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
