"""wishlists/urls.py"""
from django.urls import path
from .views import WishlistView, WishlistAddView, WishlistRemoveView, WishlistClearView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('add/', WishlistAddView.as_view(), name='wishlist-add'),
    path('remove/', WishlistRemoveView.as_view(), name='wishlist-remove'),
    path('clear/', WishlistClearView.as_view(), name='wishlist-clear'),
]
