"""
Views for core functionality.
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Item
from .serializers import ItemSerializer


class ItemListCreateView(generics.ListCreateAPIView):
    """
    List all items or create a new item.
    Items are tenant-specific - each tenant only sees their own items.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all items",
        description="Get all items in the current tenant",
        responses={200: ItemSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new item",
        description="Create a new item in the current tenant",
        request=ItemSerializer,
        responses={201: ItemSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an item.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get item details",
        description="Retrieve a specific item",
        responses={200: ItemSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update item",
        description="Update a specific item",
        request=ItemSerializer,
        responses={200: ItemSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete item",
        description="Delete a specific item",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
