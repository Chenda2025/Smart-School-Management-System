from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AcademicYear, ClassRoom, Section, Student, Teacher, Parent  # <-- add CustomUser here
from users.models import CustomUser
from core.models import Subject,Score

# Simple registration for other models
admin.site.register(AcademicYear)
admin.site.register(ClassRoom)
admin.site.register(Section)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Parent)
# admin.site.register(Score)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # List view — what you see in the main list
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_display_links = ('username', 'email')  # clickable links
    list_editable = ('is_active', 'is_staff')  # quick edit without opening
    ordering = ('username',)

    # Filters on the right sidebar
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')

    # Search box at top
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Detail view — when you click a user
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('School Role', {
            'fields': ('role',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)  # collapsible section
        }),
    )

    # Add new user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    # Make password read-only in edit (security)
    readonly_fields = ('last_login', 'date_joined')

    # Show 50 users per page
    list_per_page = 50

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'exam_type',
        'score',
        'grade',
        'recorded_by',      # <-- shows who entered the score
        'recorded_at'
    )
    list_filter = (
        'subject',
        'exam_type',
        'recorded_at',
        'recorded_by'       # <-- filter by who recorded
    )
    search_fields = (
        'student__user__first_name',
        'student__user__last_name',
        'student__user__username',
        'subject__name',
        'recorded_by__first_name',     # <-- search by teacher name
        'recorded_by__last_name',
    )
    readonly_fields = ('grade', 'recorded_at', 'recorded_by')  # auto filled

    fieldsets = (
        (None, {
            'fields': ('student', 'subject', 'exam_type')
        }),
        ('Score', {
            'fields': ('score', 'grade')
        }),
        ('Auto Filled', {
            'fields': ('recorded_by', 'recorded_at'),
            'classes': ('collapse',)  # collapsible section
        }),
    )

    # Auto fill recorded_by when creating new score
    def save_model(self, request, obj, form, change):
        if not change:  # only when creating new (not editing)
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

    # Auto calculate grade every save
    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        obj.grade = obj.calculate_grade()
        return obj

    # Show full name for recorded_by in list (instead of username)
    def get_recorded_by(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else '-'
    get_recorded_by.short_description = 'Recorded By'
    get_recorded_by.admin_order_field = 'recorded_by__first_name'