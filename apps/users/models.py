"""
User models - uses Django's default User model.
All users are tenant-specific (stored in tenant schemas).
"""
from django.contrib.auth.models import User

# We use Django's default User model
# Each tenant has its own users in their schema
