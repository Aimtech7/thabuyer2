"""tests/test_notifications.py — Notification REST API tests."""
import pytest
from django.urls import reverse
from notifications.models import Notification


def make_notification(user, title='Test', ntype='general', is_read=False):
    return Notification.objects.create(
        recipient=user,
        title=title,
        message='Test notification message.',
        notification_type=ntype,
        is_read=is_read,
    )


@pytest.mark.django_db
class TestNotificationAPI:
    def test_list_notifications(self, buyer_client, buyer):
        make_notification(buyer)
        make_notification(buyer, title='Another')
        resp = buyer_client.get(reverse('notification-list'))
        assert resp.status_code == 200
        assert resp.data['count'] == 2

    def test_unread_filter(self, buyer_client, buyer):
        make_notification(buyer, is_read=True)
        make_notification(buyer, is_read=False)
        resp = buyer_client.get(reverse('notification-list') + '?unread=true')
        assert resp.status_code == 200
        assert resp.data['count'] == 1

    def test_mark_single_notification_read(self, buyer_client, buyer):
        n = make_notification(buyer)
        url = reverse('notification-mark-read', kwargs={'pk': n.id})
        resp = buyer_client.post(url)
        assert resp.status_code == 200
        n.refresh_from_db()
        assert n.is_read is True

    def test_mark_all_read(self, buyer_client, buyer):
        make_notification(buyer)
        make_notification(buyer, title='B')
        resp = buyer_client.post(reverse('notification-read-all'))
        assert resp.status_code == 200
        assert Notification.objects.filter(recipient=buyer, is_read=False).count() == 0

    def test_delete_notification(self, buyer_client, buyer):
        n = make_notification(buyer)
        url = reverse('notification-delete', kwargs={'pk': n.id})
        resp = buyer_client.delete(url)
        assert resp.status_code == 204
        assert not Notification.objects.filter(pk=n.id).exists()

    def test_clear_all_notifications(self, buyer_client, buyer):
        make_notification(buyer)
        make_notification(buyer, title='B')
        resp = buyer_client.delete(reverse('notification-clear'))
        assert resp.status_code == 200
        assert Notification.objects.filter(recipient=buyer).count() == 0

    def test_cannot_access_other_users_notifications(self, buyer_client, seller):
        n = make_notification(seller)
        url = reverse('notification-mark-read', kwargs={'pk': n.id})
        resp = buyer_client.post(url)
        assert resp.status_code == 404

    def test_requires_authentication(self, api_client):
        resp = api_client.get(reverse('notification-list'))
        assert resp.status_code == 401
