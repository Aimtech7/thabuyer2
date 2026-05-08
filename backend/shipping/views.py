from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ShipmentTracker, TrackingEvent
from .serializers import ShipmentTrackerSerializer
from core.permissions import IsBuyer, IsSeller

class ShipmentTrackView(generics.RetrieveAPIView):
    """
    Get tracking details for an order.
    """
    serializer_class = ShipmentTrackerSerializer
    permission_classes = [IsBuyer]

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return ShipmentTracker.objects.prefetch_related('events').get(order_id=order_id)

class UpdateTrackingView(APIView):
    """
    Seller can push tracking updates manually (or webhook from EasyPost).
    """
    permission_classes = [IsSeller]

    def post(self, request, order_id):
        tracker = ShipmentTracker.objects.get(order_id=order_id)
        status = request.data.get('status')
        location = request.data.get('location', '')
        description = request.data.get('description', '')
        timestamp = request.data.get('timestamp')

        TrackingEvent.objects.create(
            tracker=tracker,
            status=status,
            location=location,
            description=description,
            timestamp=timestamp
        )

        tracker.status = status
        tracker.save(update_fields=['status'])

        return Response({'status': 'success', 'message': 'Tracking event recorded.'})
