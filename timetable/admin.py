from django.contrib import admin
from .models import ClassRoom, Subject, Day, Period, TimetableEntry


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['get_name_display']
    list_editable = []

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['number', 'start_time', 'end_time']
    list_editable = ['start_time', 'end_time']
    ordering = ['number']

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'subject', 'teacher', 'day', 'period']
    list_filter = ['classroom', 'day', 'period']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__name']