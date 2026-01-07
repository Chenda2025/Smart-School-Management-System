# core/models.py — FINAL 100% WORKING VERSION — 2025 ELITE
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator



# ─────────────────────────────────────
# ACADEMIC YEAR
# ─────────────────────────────────────
class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., 2024-2025
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


# ─────────────────────────────────────
# CLASSROOM & SECTION
# ─────────────────────────────────────
class ClassRoom(models.Model):
    name = models.CharField(max_length=20)  # Grade 10, Grade 11, etc.

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=5)  # A, B, C
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='sections')

    class Meta:
        unique_together = ('name', 'classroom')
        ordering = ['classroom__name', 'name']

    def __str__(self):
        return f"{self.classroom} - {self.name}"


# ─────────────────────────────────────
# STUDENT
# ─────────────────────────────────────
class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    roll_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9-]+$')]
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    admission_date = models.DateField(default=timezone.now)
    promoted = models.BooleanField(default=False)

    # FOR ID CARD
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['classroom__name', 'section__name', 'roll_number']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"


# ─────────────────────────────────────
# TEACHER
# ─────────────────────────────────────
class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    # subjects_taught = models.ManyToManyField('Subject', related_name='teachers', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


# ─────────────────────────────────────
# PARENT
# ─────────────────────────────────────
class Parent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    children = models.ManyToManyField(Student, related_name='parents', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Parent)"


# ─────────────────────────────────────
# SUBJECT
# ─────────────────────────────────────
class Subject(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'teacher_profile__isnull': False},
        related_name='subjects_taught'
    )

    class Meta:
        unique_together = ('name', 'classroom')
        ordering = ['classroom__name', 'name']

    def __str__(self):
        return f"{self.name} - {self.classroom}"


# ─────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    recorded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date', '-recorded_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['subject', 'date']),
        ]

    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError("Cannot mark attendance for future dates!")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.get_status_display()} ({self.date})"

    @property
    def is_absent(self):
        return self.status == 'absent'


from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from core.models import Student,Subject



# ─────────────────────────────────────
# SCORE
# ─────────────────────────────────────
class Score(models.Model):
    EXAM_TYPES = [
        ('monthly', 'Monthly Test'),      # ← NEW: Added for monthly exams
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('assignment', 'Assignment'),
        ('attendance', 'Attendance Penalty'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES,
        default='quiz'  # optional: set a default if needed
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.CharField(max_length=5, blank=True, editable=False)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_scores'
    )

    class Meta:
        unique_together = ('student', 'subject', 'exam_type')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['student', 'exam_type']),
            models.Index(fields=['subject', 'exam_type']),
            models.Index(fields=['recorded_at']),
        ]
        verbose_name = 'Score'
        verbose_name_plural = 'Scores'

    def clean(self):
        super().clean()
        if self.score is not None and not (0 <= float(self.score) <= 100):
            raise ValidationError("Score must be between 0.00 and 100.00")

    def calculate_grade(self):
        if self.score is None:
            return ''
        s = float(self.score)
        if s >= 96:
            return 'A'
        elif s >= 90:
            return 'A-'
        elif s >= 85:
            return 'B+'
        elif s >= 80:
            return 'B'
        elif s >= 75:
            return 'B-'
        elif s >= 70:
            return 'C+'
        elif s >= 65:
            return 'C'
        elif s >= 60:
            return 'C-'
        elif s >= 50:
            return 'D'
        else:
            return 'F'

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation runs
        self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject.name} ({self.get_exam_type_display()}): {self.score} → {self.grade}"

    @property
    def is_passing(self):
        return self.grade not in ['F', '']
    # ─────────────────────────────────────
# QR SESSION — FOR QR ATTENDANCE
# ─────────────────────────────────────
class QRSession(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    classroom = models.ForeignKey('ClassRoom', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = timezone.now().strftime('%Y%m%d%H%M%S%f') + str(self.pk or '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR for {self.classroom} - Expires {self.expires_at}"
    
from users.models import CustomUser
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"