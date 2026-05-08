from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Coupon, PromoPricing
from .serializers import CouponSerializer, PromoPricingSerializer
from core.permissions import IsSeller

class CouponListCreateView(generics.ListCreateAPIView):
    """Sellers can create and list their coupons."""
    serializer_class = CouponSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Coupon.objects.filter(seller=self.request.user)

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Sellers can manage a specific coupon."""
    serializer_class = CouponSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Coupon.objects.filter(seller=self.request.user)

class PromoPricingListCreateView(generics.ListCreateAPIView):
    """Sellers can create and list their promotional pricing."""
    serializer_class = PromoPricingSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return PromoPricing.objects.filter(product__seller=self.request.user)

class PromoPricingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Sellers can manage specific promotional pricing."""
    serializer_class = PromoPricingSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return PromoPricing.objects.filter(product__seller=self.request.user)
