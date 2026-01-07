# users/models.py — FINAL ELITE CUSTOMUSER — 100% WORKING
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    # ROLE
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name=_("User Role")
    )

    # BASIC INFO
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?[\d\s\-\(\)]+$')],
        verbose_name=_("Phone Number")
    )
    photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_("Profile Photo")
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name=_("Gender")
    )

    # TEACHER ONLY
    employee_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9-]+$')],
        verbose_name=_("Employee ID")
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.is_superuser or self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def is_parent(self):
        return self.role == 'parent'