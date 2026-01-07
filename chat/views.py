from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import CustomUser
from .models import ChatRoom, Message

@login_required
def chat_list(request):

    user = request.user
    print(user.id)
    
    # Get all chat rooms for this user
    chat_rooms = ChatRoom.objects.filter(
        participants=user
    ).order_by('-last_message_at', '-created_at')

    rooms_with_info = []
    for room in chat_rooms:
        # Other user for 1-on-1 chat
        other_user = None
        if not room.is_group:
            other_user = room.participants.exclude(id=user.id).first()

        # Last message
        last_message = room.messages.select_related('sender').last()

        # Unread count
        unread_count = room.messages.filter(
            is_read=False
        ).exclude(sender=user).count()

        rooms_with_info.append({
            'room': room,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    # Available users to start chat with
    available_users = CustomUser.objects.exclude(id=user.id)
    if user.role == 'student':
        available_users = available_users.filter(role__in=['teacher', 'admin'])

    context = {
        'rooms_with_info': rooms_with_info,
        'available_users': available_users.order_by('first_name'),
        'user': user,
    }

    return render(request, 'chat/chat_list.html', context)

from django.urls import reverse

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Student restriction
    if request.user.role == 'student' and other_user.role not in ['teacher', 'admin']:
        messages.error(request, "Students can only chat with teachers or admin.")
        return redirect('chat:chat_list')

    # Create or get 1-on-1 chat room
    room = ChatRoom.objects.filter(
        Q(participants=request.user) & Q(participants=other_user),
        is_group=False
    ).first()

    if not room:
        room = ChatRoom.objects.create(is_group=False)
        room.participants.add(request.user, other_user)

    # FIXED — use reverse + query param

    return redirect('chat:chat_room', room_id=room.id)
    

@login_required
def send_message(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        content = request.POST.get('content', '').strip()

        if not room_id:
            messages.error(request, "Invalid room.")
            return redirect('chat:chat_list')

        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)

        if content:
            Message.objects.create(
                chat_room=room,
                sender=request.user,
                content=content
            )
            room.update_last_message()
            messages.success(request, "Message sent!")

        # FIXED — use namespace
        return redirect('chat:chat_room', room_id=room_id)

    return redirect('chat:chat_list')

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # Access control
    if request.user not in room.participants.all():
        messages.error(request, "Access denied.")
        return redirect('chat_list')

    # Other user for 1-on-1 chat
    other_user = None
    if not room.is_group:
        other_user = room.participants.exclude(id=request.user.id).first()

    # Messages
    messages = room.messages.select_related('sender').order_by('timestamp')

    # Mark messages as read
    room.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    context = {
        'room': room,
        'other_user': other_user,
        'messages': messages,
        'teacher_user': request.user,  # if needed in template
    }

    return render(request, 'chat/chat_room.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max, Q
from django.urls import reverse

from .models import ChatRoom, Message
from users.models import CustomUser
from timetable.models import TimetableEntry
from core.models import Student, Parent


@login_required
def chat_list_teacher(request):
    teacher_user = request.user  # Now uses logged-in teacher

    # Get all chat rooms the teacher is in
    chat_rooms = ChatRoom.objects.filter(
        participants=teacher_user
    ).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    # Add unread count and other_user info to each room
    for room in chat_rooms:
        room.unread_count = room.messages.filter(
            is_read=False
        ).exclude(sender=teacher_user).count()
        room.other_user = room.participants.exclude(id=teacher_user.id).first()

    # Selected room and messages
    selected_room = None
    messages_list = []
    selected_other_user = None
    room_id = request.GET.get('room')

    if room_id:
        selected_room = get_object_or_404(
            ChatRoom,
            id=room_id,
            participants=teacher_user
        )
        messages_list = selected_room.messages.select_related(
            'sender', 'sender__profile'
        ).order_by('timestamp')
        selected_other_user = selected_room.participants.exclude(
            id=teacher_user.id
        ).first()

        # Mark incoming messages as read
        selected_room.messages.filter(
            is_read=False
        ).exclude(sender=teacher_user).update(is_read=True)

    # Handle search in "New Message" modal
    search_query = request.GET.get('search', '').strip()
    search_results = type('obj', (object,), {
        'students': [],
        'parents': [],
        'other_users': []
    })()

    if search_query:
        teacher_classes = TimetableEntry.objects.filter(
            teacher=teacher_user
        ).values_list('classroom', flat=True)

        students = Student.objects.filter(
            classroom__in=teacher_classes,
            user__first_name__icontains=search_query
        ).select_related('user', 'user__profile')

        parents = Parent.objects.filter(
            children__classroom__in=teacher_classes,
            user__first_name__icontains=search_query
        ).distinct().select_related('user', 'user__profile')

        other_users = CustomUser.objects.filter(
            (Q(role='teacher') | Q(is_staff=True)) &
            Q(first_name__icontains=search_query)
        ).exclude(id=teacher_user.id).select_related('profile')

        search_results.students = students
        search_results.parents = parents
        search_results.other_users = other_users

    context = {
        'chat_rooms': chat_rooms,
        'selected_room': selected_room,
        'selected_other_user': selected_other_user,
        'messages': messages_list,
        'teacher_user': teacher_user,
        'search_query': search_query,
        'search_results': search_results,
    }
    return render(request, 'teacher/chat.html', context)


@login_required
def send_message_teacher(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        content = request.POST.get('content', '').strip()

        if not room_id or not content:
            messages.error(request, "Invalid message or room.")
            return redirect('teacher_chat')

        room = get_object_or_404(
            ChatRoom,
            id=room_id,
            participants=request.user
        )

        Message.objects.create(
            chat_room=room,
            sender=request.user,
            content=content
        )

        return redirect(f"{reverse('teacher_chat')}?room={room_id}")

    return redirect('teacher_chat')


@login_required
def start_chat_teacher(request, user_id):
    """
    Start a 1-on-1 chat with another user (student parent, teacher, admin)
    Creates a new room if none exists.
    """
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Prevent self-chat
    if other_user == request.user:
        messages.error(request, "You cannot start a chat with yourself.")
        return redirect('teacher_chat')

    # Look for existing 1-on-1 room
    room = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).filter(
        is_group=False
    ).first()

    # Create new room if doesn't exist
    if not room:
        room = ChatRoom.objects.create(is_group=False)
        room.participants.add(request.user, other_user)

    return redirect(f"{reverse('teacher_chat')}?room={room.id}")