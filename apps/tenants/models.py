"""
Tenant models for multi-tenancy support.
"""
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Tenant(TenantMixin):
    """
    Tenant model representing each organization/client.
    Each tenant gets its own PostgreSQL schema.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Additional fields for customization
    max_users = models.IntegerField(default=10, help_text="Maximum users allowed for this tenant")

    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Domain model for tenant routing.
    Maps domains/subdomains to tenants.
    """
    pass
