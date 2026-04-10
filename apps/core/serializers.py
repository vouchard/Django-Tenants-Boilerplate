"""
Serializers for core models.
"""
from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
