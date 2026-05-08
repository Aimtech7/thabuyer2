"""api/urls.py — Central API v1 router"""
from django.urls import path, include

urlpatterns = [
    # Authentication
    path('auth/', include('users.urls')),

    # Products & Search
    path('products/', include('products.urls')),

    # Pricing & Alerts
    path('pricing/', include('pricing.urls')),

    # Cart
    path('cart/', include('cart.urls')),

    # Orders
    path('orders/', include('orders.urls')),

    # Reviews & Discussions
    path('reviews/', include('reviews.urls')),

    # Seller Dashboard
    path('seller/', include('sellers.urls')),

    # Admin Panel
    path('admin/', include('admin_panel.urls')),

    # Promotions (Coupons + Promo Pricing)
    path('promotions/', include('promotions.urls')),

    # AI Engine
    path('ai/', include('ai_engine.urls')),

    # Notifications (REST endpoints)
    path('notifications/', include('notifications.urls')),

    # Wishlists
    path('wishlist/', include('wishlists.urls')),

    # Messaging
    path('messages/', include('messaging.urls')),

    # Analytics
    path('analytics/', include('analytics.urls')),

    # Shipping & Tracking
    path('shipping/', include('shipping.urls')),
]
