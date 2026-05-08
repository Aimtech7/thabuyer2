"""notifications/serializers.py"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'related_entity_id',
            'related_entity_type',
            'is_read',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'related_entity_id',
            'related_entity_type',
            'created_at',
        ]
