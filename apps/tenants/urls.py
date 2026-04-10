"""
URL patterns for tenant management.
"""
from django.urls import path
from .views import TenantRegistrationView, TenantDetailView

app_name = 'tenants'

urlpatterns = [
    path('register/', TenantRegistrationView.as_view(), name='register'),
    path('me/', TenantDetailView.as_view(), name='detail'),
]
