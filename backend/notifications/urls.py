"""notifications/urls.py"""
from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    NotificationClearAllView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('clear/', NotificationClearAllView.as_view(), name='notification-clear'),
    path('<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<uuid:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
]
