# smart_school/ai_assistant/views.py

import json
from datetime import date, timedelta

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Conversation, Message
from .service import get_ai_response


# ==============================
# API CHAT (AJAX / FETCH)
# ==============================
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AIChatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()

            if not message:
                return JsonResponse({"error": "Message is required"}, status=400)

            response = get_ai_response(request.user, message)

            return JsonResponse({
                "response": response,
                "role": getattr(request.user, "role", "guest")
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception:
            return JsonResponse({"error": "Something went wrong"}, status=500)


# ==============================
# GROUP CONVERSATIONS BY DATE
# ==============================
def group_conversations_by_date(conversations):
    today = date.today()
    yesterday = today - timedelta(days=1)
    start_week = today - timedelta(days=today.weekday())
    start_last_week = start_week - timedelta(days=7)

    grouped = {
        "Today": [],
        "Yesterday": [],
        "This Week": [],
        "Last Week": [],
        "Earlier": [],
    }

    for convo in conversations:
        convo_date = convo.updated_at.date()

        if convo_date == today:
            grouped["Today"].append(convo)
        elif convo_date == yesterday:
            grouped["Yesterday"].append(convo)
        elif convo_date >= start_week:
            grouped["This Week"].append(convo)
        elif convo_date >= start_last_week:
            grouped["Last Week"].append(convo)
        else:
            grouped["Earlier"].append(convo)

    return grouped


# ==============================
# CHAT PAGE (HTML)
# ==============================
@login_required
def ai_chat_page(request, conversation_id=None):
    user = request.user

    conversations = Conversation.objects.filter(
        user=user
    ).order_by("-updated_at")

    grouped_conversations = group_conversations_by_date(conversations)

    current_conversation = None
    messages = []

    if conversation_id:
        current_conversation = get_object_or_404(
            Conversation, id=conversation_id, user=user
        )
        messages = current_conversation.messages.order_by("timestamp")

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if not user_message:
            return redirect("ai_chat_page", conversation_id=conversation_id)

        # 🟢 Create chat only when sending first message
        if not current_conversation:
            current_conversation = Conversation.objects.create(
                user=user,
                title="New Chat"
            )

        # Save user message
        Message.objects.create(
            conversation=current_conversation,
            content=user_message,
            is_bot=False
        )

        # 🧠 AUTO-RENAME (ONLY FIRST MESSAGE)
        if current_conversation.title == "New Chat":
            clean_title = user_message.replace("?", "").strip()
            current_conversation.title = clean_title[:40]

        current_conversation.save()

        # AI reply
        ai_reply = get_ai_response(user, user_message)

        Message.objects.create(
            conversation=current_conversation,
            content=ai_reply,
            is_bot=True
        )

        return redirect("ai_chat_page", conversation_id=current_conversation.id)

    return render(request, "ai_assistant/chat_page.html", {
        "grouped_conversations": grouped_conversations,
        "current_conversation": current_conversation,
        "messages": messages,
    })


# ==============================
# NEW CHAT BUTTON
# ==============================
@login_required
def ai_new_chat(request):
    convo = Conversation.objects.create(
        user=request.user,
        title="New Chat"
    )
    return redirect("ai_chat_page", conversation_id=convo.id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Conversation

@login_required
def ai_delete_chat(request, conversation_id):
    convo = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    convo.delete()
    return redirect("ai_chat_page")  # Redirect to main chat page
