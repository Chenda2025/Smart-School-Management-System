# academics/admin.py
from django.contrib import admin
# from core.models import Score
# from .models import Exam


# @admin.register(Exam)
# class ExamAdmin(admin.ModelAdmin):
#     list_display = ('name', 'exam_type', 'date', 'classroom')
#     list_filter = ('exam_type', 'classroom')


# @admin.register(Score)
# class ScoreAdmin(admin.ModelAdmin):
#     list_display = ('student', 'subject', 'exam', 'marks', 'grade')
#     list_filter = ('exam', 'subject')
#     readonly_fields = ('grade',)
    
#     def has_add_permission(self, request, obj=None):
#         return True

#     def has_change_permission(self, request, obj=None):
#         return True