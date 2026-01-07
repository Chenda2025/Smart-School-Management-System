from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.is_group:
            return self.name or "Group Chat"
        return " & ".join([p.get_full_name() for p in self.participants.all()])

    def update_last_message(self):
        latest = self.messages.order_by('-timestamp').first()
        if latest:
            self.last_message_at = latest.timestamp
            self.save(update_fields=['last_message_at'])

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)  # text message
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)  # image
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)  # file
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)  # for edit
    deleted = models.BooleanField(default=False)  # soft delete

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content or 'Media'}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

# Add this method to ChatRoom
def create_class_group(classroom):
    """ Create group chat for a class """
    room, created = ChatRoom.objects.get_or_create(
        name=f"{classroom.name} Group",
        is_group=True
    )
    if created:
        # Add all students in class
        room.participants.add(*classroom.students.all().values_list('user', flat=True))
        # Add teacher(s)
        room.participants.add(*classroom.timetable_entries.values_list('teacher', flat=True).distinct())
    return room