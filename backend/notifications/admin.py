"""notifications/admin.py"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['recipient__email', 'title', 'message']
    readonly_fields = ['recipient', 'title', 'message', 'notification_type',
                       'related_entity_id', 'related_entity_type', 'created_at']
    ordering = ['-created_at']
    actions = ['mark_all_read']

    def mark_all_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_all_read.short_description = 'Mark selected as read'
