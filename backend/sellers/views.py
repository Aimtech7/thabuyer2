"""sellers/views.py"""
from decimal import Decimal
from django.db.models import Sum, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.permissions import IsSeller, IsSellerOrAdmin
from .models import SellerProfile
from .serializers import (
    SellerProfileSerializer,
    SellerProfileCreateSerializer,
    SellerDashboardSerializer,
)


class SellerProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the current seller's profile."""
    permission_classes = [IsSeller]
    serializer_class = SellerProfileSerializer

    def get_object(self):
        return self.request.user.seller_profile


class SellerProfileCreateView(generics.CreateAPIView):
    """Create a seller profile for a user with Seller role."""
    permission_classes = [IsSeller]
    serializer_class = SellerProfileCreateSerializer


class SellerDashboardView(APIView):
    """Aggregated dashboard data for the current seller."""
    permission_classes = [IsSeller]

    def get(self, request):
        user = request.user
        profile = user.seller_profile

        products = user.products.all()
        total_products = products.count()

        # Aggregate order data across all seller products
        from orders.models import OrderItem
        order_items = OrderItem.objects.filter(
            product__seller=user
        ).select_related('order')

        total_orders = order_items.values('order').distinct().count()
        revenue_data = order_items.filter(
            order__status__in=['processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('subtotal'))
        total_revenue = revenue_data['total'] or Decimal('0.00')

        pending_orders = order_items.filter(order__status='pending').values('order').distinct().count()

        from reviews.models import Review
        recent_reviews = Review.objects.filter(
            product__seller=user
        ).select_related('buyer', 'product').order_by('-created_at')[:5]

        from reviews.serializers import ReviewSerializer
        review_data = ReviewSerializer(recent_reviews, many=True).data

        # Analytics
        analytics = products.aggregate(
            total_views=Sum('views_count'),
            total_clicks=Sum('clicks_count')
        )
        total_views = analytics['total_views'] or 0
        total_clicks = analytics['total_clicks'] or 0

        # Stale products
        from django.utils import timezone
        from datetime import timedelta
        threshold_date = timezone.now() - timedelta(days=30)
        stale_products_count = products.filter(updated_at__lt=threshold_date, is_active=True).count()

        return Response({
            'status': 'success',
            'data': {
                'profile': SellerProfileSerializer(profile).data,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': str(total_revenue),
                'pending_orders': pending_orders,
                'recent_reviews': review_data,
                'total_views': total_views,
                'total_clicks': total_clicks,
                'stale_products_count': stale_products_count,
            },
        })


class SellerProductsView(generics.ListAPIView):
    """List all products owned by the current seller."""
    permission_classes = [IsSeller]

    def get_queryset(self):
        from products.models import Product
        return Product.objects.filter(seller=self.request.user).prefetch_related('images')

    def list(self, request, *args, **kwargs):
        from products.serializers import ProductSerializer
        queryset = self.get_queryset()
        serializer = ProductSerializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data})
