"""
smartSchool/urls.py — FINAL CLEAN VERSION 2025
Elite School Management System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

# === VIEW IMPORTS ===
from student.views import (
    student_dashboard,
    my_report_card,
    my_id_card, 
    my_attendance,
    my_timetable,
)
from timetable.views import assign_timetable
from django.urls import path, include
from chat.views import (
    chat_list_teacher,
    start_chat,
    send_message,
    chat_list_teacher,
    send_message_teacher,
    start_chat_teacher,
)
from reports.views import (
    generate_report_card_pdf,
    generate_id_card,
    export_scores_excel,
    report_list,
    staff_dashboard,
    report_card, 
    id_card,
    qr_scan,
    qr_scan_process,
    send_notification,
    teacher_dashboard,
    teacher_timetable,
    teacher_subjects,
    my_classes,
    manual_attendance,
    qr_attendance,
    qr_scan,
    teacher_enter_scores,
    view_student_scores,
    my_profile,
    my_notifications,
    mark_notification_read,
    mark_notification_read_all,
    mark_all_notifications_read,
    teacher_notifications
)
from users.views import (
    all_users_list, 
    user_profile, 
    edit_profile, 
    add_user,
    # custom_login

    )
from core.views import (
    add_student,
    add_teacher,
    bulk_import,
    bulk_import_preview,
    classes_list,
    subjects_list,
    enter_scores,
    legacy_scores,
    mark_attendance,
    analytics_dashboard,
    performance_dashboard,
    student_info,
    edit_attendance,
    delete_attendance,
    export_attendance_excel, 
    export_attendance_word,
    qr_attendance_home,
    create_qr_session,
    qr_scan_view,
    CustomLoginView

)

# Helper redirect
def redirect_export(request):
    return redirect('export_excel')


urlpatterns = [
   # ROOT → LOGIN PAGE FIRST
path('', CustomLoginView.as_view(), name='root_login'),  # optional

# AUTH
path('login/', CustomLoginView.as_view(), name='login'),
path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

# ADMIN PANEL
path('admin/', admin.site.urls),

# MAIN DASHBOARDS
path('staff/', staff_dashboard, name='staff_dashboard'),
path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
path('student/dashboard', student_dashboard, name='student_dashboard'),
# path('parent/dashboard/', parent_dashboard, name='parent_dashboard'),

    # ANALYTICS & PERFORMANCE
    path('performance/', performance_dashboard, name='performance_dashboard'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('legacy-scores/', legacy_scores, name='legacy_scores'),

    # ACADEMIC TOOLS
    path('enter-scores/', enter_scores, name='enter_scores'),
    path('mark-attendance/', mark_attendance, name='mark_attendance'),
    path('classes/', classes_list, name='classes_list'),
    path('subjects/', subjects_list, name='subjects_list'),

    # USER MANAGEMENT
    path('users/all/', all_users_list, name='all_users_list'),
    path('users/add/', add_user, name='add_user'),
    path('profile/<int:pk>/', user_profile, name='user_profile'),
    path('profile/<int:pk>/edit/', edit_profile, name='edit_profile'),

    # ADD USERS
    path('add-student/', add_student, name='add_student'),
    path('add-teacher/', add_teacher, name='add_teacher'),

    # BULK IMPORT
    path('bulk-import/', bulk_import, name='bulk_import'),
    path('bulk-import/preview/', bulk_import_preview, name='bulk_import_preview'),

    path('reports/', report_list, name='report_list'),
    path('reports/card/<int:student_id>/', report_card, name='report_card'),  # HTML view

    path('reports/pdf/<int:student_id>/', generate_report_card_pdf, name='report_card_pdf'),  # PDF download
    path('reports/id-card/<int:student_id>/', generate_id_card, name='id_card'),

    # DATA EXPORT
    path('export/', export_scores_excel, name='export_excel'),
    path('export/excel/', export_scores_excel),
    path('export', redirect_export),
    path('student-info/', student_info, name='student_info'),
    path('attendance/edit/<int:pk>/', edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:pk>/',delete_attendance, name='delete_attendance'),
    path('export-attendance/excel/', export_attendance_excel, name='export_attendance_excel'),
    path('export-attendance/word/', export_attendance_word, name='export_attendance_word'),
    # urls.py
    
    path('qr-attendance/',qr_attendance_home, name='qr_attendance_home'),
    path('qr/create/', create_qr_session, name='create_qr_session'),
    path('qr/scan/<str:token>/',qr_scan_view, name='qr_scan'),

    # generate ID card 
    path('id-card/<int:user_id>/', id_card, name='id_card'),
    path('qr-scan/', qr_scan, name='qr_scan'),
    path('qr-scan-process/', qr_scan_process, name='qr_scan_process'),
    path('send-notification/', send_notification, name='send_notification'),
    path('my-notifications/', my_notifications, name='my_notifications'),
    path('teacher-notifications/', teacher_notifications, name='teacher_notifications'),
    path('ajax/mark-notification-read/',mark_notification_read, name='mark_notification_read'),
    path('my-notification/mark-read/<int:pk>/', mark_notification_read_all, name='mark_notification_read_all'),
    path('my-notification/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),

    path('chat/', include('chat.urls')),
    path('send/', send_message, name='send_message'),


# part dashboard teacher
    path('assign_timetable/', assign_timetable, name='assign_timetable'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/timetable/', teacher_timetable, name='teacher_timetable'),
    path('teacher/subjects/', teacher_subjects, name='teacher_subjects'),
    path('teacher/my-classes/', my_classes, name='teacher_my_classes'),
    path('teacher/attendance/manual/', manual_attendance, name='teacher_attendance_manual'),
    path('teacher/qr-attendance/', qr_attendance, name='teacher_qr_attendance'),
    # path('qr-scan/', qr_scan_view, name='qr_scan'),
    path('export-attendance/', export_attendance_excel, name='export_attendance_excel'),
    path('teacher/enter-score', teacher_enter_scores, name='teacher_enter_scores'),
    path('teacher/student/<int:student_id>/scores/', view_student_scores, name='view_student_scores'),
    path('teacher/chat/', chat_list_teacher, name='teacher_chat'),
    # path('teacher/chat/',chat_list_teacher, name='teacher_chat'),
    path('teacher/send-message/', send_message_teacher, name='send_message_teacher'),
    path('teacher/start-chat-teacher/<int:user_id>/',start_chat_teacher, name='start_chat_teacher'),
    # path('teacher/chat/start/<int:user_id>/', start_chat, name='start_chat'),
    path('teacher/profile/', my_profile, name='my_profile'),

    path('ai/', include('ai_assistant.urls')),

    # STUDENT DASHBOARD
    path('student/dashboard/', student_dashboard, name='student_dashboard'),

    # MY REPORT CARD
    path('my-report-card/', my_report_card, name='my_report_card'),

    # # MY ID CARD
    # core/urls.py
    path('my-id-card/<int:student_id>/', my_id_card, name='my_id_card'),

    # # MY ATTENDANCE (optional separate page)
    path('my-attendance/', my_attendance, name='my_attendance'),
    # # MY TIMETABLE (optional)
    path('my-timetable/', my_timetable, name='my_timetable'),
  

    # # MESSAGES / CHAT
    path('student/', include('student.urls')),
    


    # # STUDENT INFO (existing)
    # path('student-info/', views.student_info, name='student_info'),

]

# SERVE MEDIA & STATIC IN DEVELOPMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)