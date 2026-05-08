import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from users.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        sender_id = self.scope['user'].id

        if not message_text:
            return

        # Save message to database
        saved_msg = await self.save_message(sender_id, message_text)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': str(sender_id),
                'sender_name': self.scope['user'].name,
                'created_at': saved_msg.created_at.isoformat()
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, text):
        user = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=self.conversation_id)
        msg = Message.objects.create(
            conversation=conversation,
            sender=user,
            text=text
        )
        # Update conversation timestamp
        conversation.save()
        return msg
