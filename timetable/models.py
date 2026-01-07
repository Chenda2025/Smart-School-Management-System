from django.db import models
from users.models import CustomUser
from core.models import ClassRoom,Subject


class Period(models.Model):
    number = models.PositiveIntegerField()  # 1, 2, 3...
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Period {self.number} ({self.start_time} - {self.end_time})"

class Day(models.Model):
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=10, choices=DAYS, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.get_name_display()

class TimetableEntry(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        limit_choices_to={'role': 'teacher'},  # good for production
    )
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='timetable_entries')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='timetable_entries')

    class Meta:
        unique_together = ('classroom', 'day', 'period')  # genius — no double booking
        ordering = ['day__id', 'period__number']

    def __str__(self):
        return f"{self.classroom} - {self.subject} ({self.teacher.get_full_name()}) - {self.day} Period {self.period}"