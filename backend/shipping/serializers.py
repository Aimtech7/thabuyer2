from rest_framework import serializers
from .models import ShipmentTracker, TrackingEvent

class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = ['status', 'location', 'description', 'timestamp']

class ShipmentTrackerSerializer(serializers.ModelSerializer):
    events = TrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = ShipmentTracker
        fields = ['order', 'tracking_number', 'carrier', 'status', 'estimated_delivery', 'events', 'updated_at']
