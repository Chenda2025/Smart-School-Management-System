# smart_school/ai_assistant/urls.py

from django.urls import path
from .views import (
    AIChatView,
    ai_chat_page,
    ai_new_chat,
    ai_delete_chat
)

urlpatterns = [
    path("api/chat/", AIChatView.as_view(), name="ai_chat"),

    path("chat/", ai_chat_page, name="ai_chat_page"),
    path("chat/<int:conversation_id>/", ai_chat_page, name="ai_chat_page"),

    path("chat/new/", ai_new_chat, name="ai_new_chat"),
    path('chat/delete/<int:conversation_id>/', ai_delete_chat, name='ai_delete_chat'),
]
