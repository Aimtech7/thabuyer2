"""wishlists/admin.py"""
from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ['product', 'added_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'item_count', 'created_at']
    readonly_fields = ['buyer', 'created_at']
    inlines = [WishlistItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'wishlist', 'added_at']
    list_select_related = ['wishlist__buyer', 'product']
    readonly_fields = ['added_at']
