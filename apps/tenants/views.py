"""
Views for tenant registration and management.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from .models import Tenant
from .serializers import TenantRegistrationSerializer, TenantSerializer


class TenantRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for tenant registration.
    Creates a new tenant with its own schema, domain, and admin user.
    """
    permission_classes = [AllowAny]
    serializer_class = TenantRegistrationSerializer

    @extend_schema(
        summary="Register new tenant",
        description="Create a new tenant organization with admin user. This is a public endpoint.",
        request=TenantRegistrationSerializer,
        responses={201: TenantSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(
            {
                'message': 'Tenant created successfully',
                'tenant': TenantSerializer(result['tenant']).data,
                'domain': result['domain'],
            },
            status=status.HTTP_201_CREATED
        )


class TenantDetailView(generics.RetrieveAPIView):
    """
    Get current tenant information.
    Only accessible by authenticated users within their tenant.
    """
    serializer_class = TenantSerializer

    @extend_schema(
        summary="Get current tenant details",
        description="Retrieve information about the current tenant",
        responses={200: TenantSerializer}
    )
    def get_object(self):
        from django.db import connection
        return connection.tenant
