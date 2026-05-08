import uuid
from django.db import models
from orders.models import Order


class ShipmentTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipment"
    )
    tracking_number = models.CharField(max_length=255, unique=True)
    carrier = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="label_created")
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipment_trackers"

    def __str__(self):
        return f"Shipment {self.tracking_number} ({self.carrier})"


class TrackingEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracker = models.ForeignKey(
        ShipmentTracker, on_delete=models.CASCADE, related_name="events"
    )
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = "tracking_events"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.status} at {self.timestamp}"
