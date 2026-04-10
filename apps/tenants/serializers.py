"""
Serializers for tenant registration and management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant, Domain

User = get_user_model()


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for tenant information."""

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'schema_name', 'description', 'is_active', 'created_on', 'max_users']
        read_only_fields = ['id', 'schema_name', 'created_on']


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for domain information."""

    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary']
        read_only_fields = ['id']


class TenantRegistrationSerializer(serializers.Serializer):
    """
    Serializer for public tenant registration.
    Creates a new tenant with domain and admin user.
    """
    # Tenant details
    tenant_name = serializers.CharField(max_length=100)
    schema_name = serializers.CharField(
        max_length=63,
        help_text="Unique identifier for the tenant (lowercase, no spaces)"
    )
    domain = serializers.CharField(
        max_length=253,
        help_text="Subdomain for the tenant (e.g., 'acme' for acme.yourdomain.com)"
    )

    # Admin user details
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(max_length=30, required=False)
    admin_last_name = serializers.CharField(max_length=30, required=False)

    def validate_schema_name(self, value):
        """Ensure schema name is unique and valid."""
        value = value.lower().replace(' ', '_')

        if value == 'public':
            raise serializers.ValidationError("Schema name 'public' is reserved.")

        if Tenant.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("A tenant with this schema name already exists.")

        return value

    def validate_domain(self, value):
        """Ensure domain is unique."""
        value = value.lower()

        if Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("This domain is already taken.")

        return value

    def create(self, validated_data):
        """Create tenant, domain, and admin user."""
        from django.db import connection

        # Create tenant
        tenant = Tenant.objects.create(
            name=validated_data['tenant_name'],
            schema_name=validated_data['schema_name'],
        )

        # Create domain
        Domain.objects.create(
            tenant=tenant,
            domain=validated_data['domain'],
            is_primary=True
        )

        # Switch to tenant schema and create admin user
        connection.set_tenant(tenant)

        admin_user = User.objects.create_user(
            username=validated_data['admin_email'],
            email=validated_data['admin_email'],
            password=validated_data['admin_password'],
            first_name=validated_data.get('admin_first_name', ''),
            last_name=validated_data.get('admin_last_name', ''),
            is_staff=True,
            is_superuser=True
        )

        # Switch back to public schema
        connection.set_schema_to_public()

        return {
            'tenant': tenant,
            'domain': validated_data['domain'],
            'admin_user': admin_user
        }
