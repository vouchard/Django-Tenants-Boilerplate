"""
Core models - Example tenant-specific models.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    """
    Example model to demonstrate tenant data isolation.
    Each tenant has its own items stored in their schema.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
