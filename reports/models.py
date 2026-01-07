from django.db import models
from django.contrib.auth import get_user_model
from core.models import ClassRoom

User = get_user_model()

class Notification(models.Model):
    RECIPIENT_CHOICES = [
        ('all', 'All Users'),
        ('students', 'All Students'),
        ('teachers', 'All Teachers'),
        ('class', 'Specific Class'),
        ('individual', 'Individual User'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all')
    
    # Optional fields
    specific_class = models.ForeignKey(
        ClassRoom, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications'
    )
    specific_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='received_notifications'
    )
    
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='sent_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} ({self.get_recipient_type_display()})"

    def get_recipients(self):
        """Returns queryset of users who should receive this notification"""
        if self.recipient_type == 'all':
            return User.objects.all()
        elif self.recipient_type == 'students':
            return User.objects.filter(role='student')
        elif self.recipient_type == 'teachers':
            return User.objects.filter(role='teacher')
        elif self.recipient_type == 'class' and self.specific_class:
            return User.objects.filter(role='student', student_profile__classroom=self.specific_class)
        elif self.recipient_type == 'individual' and self.specific_user:
            return User.objects.filter(pk=self.specific_user.pk)
        return User.objects.none()


class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='read_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('notification', 'user')
        verbose_name = "Notification Read Status"

    def __str__(self):
        return f"{self.user} read '{self.notification.title}'"