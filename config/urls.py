"""
URL configuration for multi-tenant boilerplate.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API Endpoints
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/core/', include('apps.core.urls')),
]
