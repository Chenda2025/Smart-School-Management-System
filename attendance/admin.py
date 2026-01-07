# attendance/admin.py
from django.contrib import admin
from core.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status')
    list_filter = ('subject', 'date', 'status')
    search_fields = ('student__user__first_name', 'student__user__last_name')