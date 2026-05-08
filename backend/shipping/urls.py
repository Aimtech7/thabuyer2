from django.urls import path
from .views import ShipmentTrackView, UpdateTrackingView

app_name = 'shipping'

urlpatterns = [
    path('track/<uuid:order_id>/', ShipmentTrackView.as_view(), name='track-shipment'),
    path('update/<uuid:order_id>/', UpdateTrackingView.as_view(), name='update-tracking'),
]
