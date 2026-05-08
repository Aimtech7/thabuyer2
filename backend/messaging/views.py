from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.permissions import IsBuyer, IsSeller

class ConversationListView(generics.ListCreateAPIView):
    """
    List all conversations for the authenticated user.
    Buyers see chats with sellers, Sellers see chats with buyers.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(buyer=user) | Q(seller=user))

    def perform_create(self, serializer):
        # Default creation logic (usually triggered by buyer)
        serializer.save()

class MessageHistoryView(generics.ListAPIView):
    """
    Get paginated message history for a specific conversation.
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        user = self.request.user
        # Verify user belongs to this conversation
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__in=Conversation.objects.filter(Q(buyer=user) | Q(seller=user))
        ).order_by('created_at')

class MarkReadView(APIView):
    """
    Mark all messages in a conversation as read for the current user.
    """
    def post(self, request, conversation_id):
        user = request.user
        Message.objects.filter(
            conversation_id=conversation_id,
            is_read=False
        ).exclude(sender=user).update(is_read=True)
        return Response({'status': 'success', 'message': 'Messages marked as read.'})
