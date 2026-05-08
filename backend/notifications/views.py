"""notifications/views.py"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/v1/notifications/
    List all notifications for the authenticated user, newest first.
    Supports ?unread=true to filter only unread notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        unread_only = self.request.query_params.get('unread', '').lower() == 'true'
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'unread_count': queryset.filter(is_read=False).count(),
            'results': serializer.data,
        })


class NotificationMarkReadView(APIView):
    """
    POST /api/v1/notifications/<id>/read/
    Mark a single notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'success', 'message': 'Notification marked as read.'})


class NotificationMarkAllReadView(APIView):
    """
    POST /api/v1/notifications/read-all/
    Mark all of the user's notifications as read at once.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({
            'status': 'success',
            'message': f'{updated} notification(s) marked as read.',
        })


class NotificationDeleteView(APIView):
    """
    DELETE /api/v1/notifications/<id>/
    Delete a single notification owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationClearAllView(APIView):
    """
    DELETE /api/v1/notifications/clear/
    Delete all notifications for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(recipient=request.user).delete()
        return Response({
            'status': 'success',
            'message': f'{deleted_count} notification(s) deleted.',
        })
