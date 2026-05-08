import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from shipping.models import ShipmentTracker, TrackingEvent
from orders.models import Order

@pytest.mark.django_db
class TestShipping:
    def test_track_shipment(self, buyer_client, buyer):
        order = Order.objects.create(buyer=buyer, total_amount=10.00, status='shipped')
        tracker = ShipmentTracker.objects.create(
            order=order,
            tracking_number="TEST123456",
            carrier="TestCarrier"
        )
        
        url = reverse('shipping:track-shipment', kwargs={'order_id': order.id})
        response = buyer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['tracking_number'] == "TEST123456"

    def test_update_tracking(self, seller_client, seller_user, buyer):
        order = Order.objects.create(buyer=buyer, total_amount=10.00, status='shipped')
        tracker = ShipmentTracker.objects.create(
            order=order,
            tracking_number="TEST123456",
            carrier="TestCarrier"
        )
        
        url = reverse('shipping:update-tracking', kwargs={'order_id': order.id})
        data = {
            'status': 'in_transit',
            'location': 'New York, NY',
            'timestamp': timezone.now().isoformat()
        }
        response = seller_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        tracker.refresh_from_db()
        assert tracker.status == 'in_transit'
        assert TrackingEvent.objects.filter(tracker=tracker).count() == 1
