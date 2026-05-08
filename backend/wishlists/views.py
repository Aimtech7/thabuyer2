"""wishlists/views.py"""
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.permissions import IsBuyer
from products.models import Product
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer


def _get_or_create_wishlist(user):
    """Helper: retrieve or lazily create the buyer's wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(buyer=user)
    return wishlist


class WishlistView(APIView):
    """
    GET  /api/v1/wishlist/   — Retrieve the current buyer's wishlist.
    """
    permission_classes = [IsBuyer]

    def get(self, request):
        wishlist = _get_or_create_wishlist(request.user)
        serializer = WishlistSerializer(wishlist)
        return Response({'status': 'success', 'data': serializer.data})


class WishlistAddView(APIView):
    """
    POST /api/v1/wishlist/add/
    Body: { "product_id": "<uuid>" }
    Add a product to the buyer's wishlist. Idempotent — adding twice returns 200.
    """
    permission_classes = [IsBuyer]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'status': 'error', 'message': 'product_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Product not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        wishlist = _get_or_create_wishlist(request.user)
        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist, product=product
        )
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({
            'status': 'success',
            'message': 'Added to wishlist.' if created else 'Already in wishlist.',
            'data': WishlistItemSerializer(item).data,
        }, status=http_status)


class WishlistRemoveView(APIView):
    """
    DELETE /api/v1/wishlist/remove/
    Body: { "product_id": "<uuid>" }
    Remove a product from the buyer's wishlist.
    """
    permission_classes = [IsBuyer]

    def delete(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'status': 'error', 'message': 'product_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        wishlist = _get_or_create_wishlist(request.user)
        deleted_count, _ = WishlistItem.objects.filter(
            wishlist=wishlist, product_id=product_id
        ).delete()
        if deleted_count == 0:
            return Response(
                {'status': 'error', 'message': 'Item not in wishlist.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'status': 'success', 'message': 'Removed from wishlist.'})


class WishlistClearView(APIView):
    """
    DELETE /api/v1/wishlist/clear/
    Remove all items from the buyer's wishlist.
    """
    permission_classes = [IsBuyer]

    def delete(self, request):
        wishlist = _get_or_create_wishlist(request.user)
        deleted_count, _ = wishlist.items.all().delete()
        return Response({
            'status': 'success',
            'message': f'{deleted_count} item(s) removed from wishlist.',
        })
