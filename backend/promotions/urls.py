from django.urls import path
from .views import (
    CouponListCreateView,
    CouponDetailView,
    PromoPricingListCreateView,
    PromoPricingDetailView
)

urlpatterns = [
    path('coupons/', CouponListCreateView.as_view(), name='coupon-list-create'),
    path('coupons/<uuid:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
    path('promopricing/', PromoPricingListCreateView.as_view(), name='promopricing-list-create'),
    path('promopricing/<uuid:pk>/', PromoPricingDetailView.as_view(), name='promopricing-detail'),
]
