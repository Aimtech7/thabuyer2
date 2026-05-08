from django.urls import path
from .views import ConversationListView, MessageHistoryView, MarkReadView

app_name = 'messaging'

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/messages/', MessageHistoryView.as_view(), name='message-history'),
    path('conversations/<uuid:conversation_id>/read/', MarkReadView.as_view(), name='mark-read'),
]
