import pytest
from django.urls import reverse
from rest_framework import status
from messaging.models import Conversation, Message

@pytest.mark.django_db
class TestMessaging:
    def test_create_conversation(self, buyer_client, seller_user, buyer):
        url = reverse('messaging:conversation-list')
        data = {
            'buyer': str(buyer.id),
            'seller': str(seller_user.id)
        }
        response = buyer_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Conversation.objects.count() == 1

    def test_list_conversations(self, buyer_client, seller_user, buyer):
        # Create a conversation manually
        Conversation.objects.create(buyer=buyer, seller=seller_user)
        
        url = reverse('messaging:conversation-list')
        response = buyer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_message_history(self, buyer_client, seller_user, buyer):
        conv = Conversation.objects.create(buyer=buyer, seller=seller_user)
        Message.objects.create(conversation=conv, sender=buyer, text="Hello Seller")
        Message.objects.create(conversation=conv, sender=seller_user, text="Hello Buyer")

        url = reverse('messaging:message-history', kwargs={'conversation_id': conv.id})
        response = buyer_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_mark_read(self, seller_client, seller_user, buyer):
        conv = Conversation.objects.create(buyer=buyer, seller=seller_user)
        msg = Message.objects.create(conversation=conv, sender=buyer, text="Unread message")
        assert not msg.is_read

        url = reverse('messaging:mark-read', kwargs={'conversation_id': conv.id})
        response = seller_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        msg.refresh_from_db()
        assert msg.is_read
