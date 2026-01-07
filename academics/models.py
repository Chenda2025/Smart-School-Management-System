from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
# from core.models import ClassRoom, Section, Teacher, Student, Subject

class Exam(models.Model):
    EXAM_TYPES = (
        ('monthly', 'Monthly'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
    )
#     name = models.CharField(max_length=50)
#     exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
#     date = models.DateField()
#     classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.name} ({self.get_exam_type_display()})"

