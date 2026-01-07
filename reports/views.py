# reports/views.py — MAC COMPATIBLE / FIXED QR ERROR

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from django.utils import timezone
from core.models import Score
from core.models import Student
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from core.models import Student
from core.models import Attendance
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Avg, Count
from core.views import Score,Subject,Student



# ===================================================
# 2) STUDENT ID CARD (PDF + QR)
# ===================================================
def generate_id_card(request, student_id):
    student = Student.objects.get(id=student_id)

    buffer = BytesIO()

    # Make QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(
        f"Student: {student.user.get_full_name()}\n"
        f"Roll: {student.roll_number}\n"
        f"Class: {student.classroom}"
    )
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Convert QR → ImageReader (IMPORTANT FIX)
    qr_reader = ImageReader(qr_buffer)

    # Create ID Card PDF
    p = canvas.Canvas(buffer, pagesize=(3.5*inch, 2.2*inch))
    width, height = 3.5*inch, 2.2*inch

    # Background
    p.setFillColorRGB(0.05, 0.05, 0.2)
    p.rect(0, 0, width, height, fill=1)

    # Title
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(0.7*inch, 1.8*inch, "ELITE SCHOOL 2025")

    # Student Data
    p.setFont("Helvetica-Bold", 11)
    p.drawString(0.7*inch, 1.5*inch, student.user.get_full_name())

    p.setFont("Helvetica", 10)
    p.drawString(0.7*inch, 1.3*inch, f"Roll: {student.roll_number}")
    p.drawString(0.7*inch, 1.1*inch, f"Class: {student.classroom}")

    if student.section:
        p.drawString(0.7*inch, 0.9*inch, f"Section: {student.section}")

    # Draw QR Code (NOW WORKS)
    p.drawImage(qr_reader, 2.3*inch, 0.7*inch, width=1*inch, height=1*inch)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.roll_number}_ID_Card.pdf"'
    return response



# ===================================================
# 3) EXCEL EXPORT
# ===================================================
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
@login_required
def export_scores_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=scores_elite_school.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = "Student Scores"

    # Headers
    headers = ['Student ID', 'Name', 'Roll No', 'Class', 'Subject', 'Exam Type', 'Score', 'Grade', 'Recorded Date']
    ws.append(headers)

    # Data
    scores = Score.objects.select_related('student__user', 'student__classroom', 'subject').all()

    for score in scores:
        row = [
            score.student.id,
            score.student.user.get_full_name(),
            score.student.roll_number,
            score.student.classroom.name,
            score.subject.name,
            score.get_exam_type_display(),  # <-- FIXED: use display
            score.score,
            score.grade,
            score.recorded_at.strftime('%Y-%m-%d')
        ]
        ws.append(row)

    wb.save(response)
    return response






from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from core.models import Student, Score

def staff_dashboard(request):
    today = timezone.now().date()

    # Basic stats
    total_students = Student.objects.count()

    # Attendance today
    attendance_percent = 0
    present_today = 0
    try:
        from attendance.models import Attendance
        present_today = Attendance.objects.filter(date=today, status='Present').count()
        attendance_percent = round((present_today / total_students * 100), 1) if total_students > 0 else 0
    except ImportError:
        pass

    # === FIXED HERE ===
    top_students = Student.objects.filter(
        scores__isnull=False  # ← changed from score__isnull
    ).annotate(
        avg_score=Avg('scores__score')  # ← changed from score__score
    ).select_related(
        'user', 'classroom', 'section'
    ).order_by('-avg_score')[:10]

    weak_students = Student.objects.filter(
        scores__isnull=False
    ).annotate(
        avg_score=Avg('scores__score')
    ).select_related(
        'user', 'classroom', 'section'
    ).filter(
        avg_score__lt=70  # adjust threshold as needed
    ).order_by('avg_score')[:10]

    # Optional: Add these if you want in stats
    total_teachers = CustomUser.objects.filter(role='teacher').count()  # adjust based on your user model

    context = {
        'total_students': total_students,
        'present_today': present_today,
        'attendance_percent': attendance_percent,
        'total_teachers': total_teachers,
        'top_students': top_students,
        'weak_students': weak_students,
        'today': today,
    }

    return render(request, 'reports/staff_dashboard.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas

from core.models import Student, Subject, Score

@login_required
def report_list(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    students = Student.objects.all().select_related('user', 'classroom').order_by('user__first_name', 'user__last_name')
    context = {'students': students}
    return render(request, 'reports/report_list.html', context)


@login_required
def report_card(request, student_id):
    """On-screen report card with print button (HTML view)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    student = get_object_or_404(Student, id=student_id)

    subjects = Subject.objects.filter(classroom=student.classroom).order_by('name')
    scores = Score.objects.filter(student=student).select_related('subject')

    subject_scores = []
    total_average = 0
    subject_count = 0

    for subject in subjects:
        midterm = scores.filter(subject=subject, exam_type='midterm').first()
        final = scores.filter(subject=subject, exam_type='final').first()
        quiz = scores.filter(subject=subject, exam_type='quiz').first()
        assignment = scores.filter(subject=subject, exam_type='assignment').first()

        score_values = []
        if midterm: score_values.append(float(midterm.score))
        if final: score_values.append(float(final.score))
        if quiz: score_values.append(float(quiz.score))
        if assignment: score_values.append(float(assignment.score))

        avg = sum(score_values) / len(score_values) if score_values else 0
        avg = round(avg, 1)

        subject_scores.append({
            'subject': subject,
            'midterm': midterm,
            'final': final,
            'quiz': quiz,
            'assignment': assignment,
            'average': avg,
            'letter_grade': get_letter_grade(avg),
        })

        total_average += avg
        subject_count += 1

    overall_average = round(total_average / subject_count, 1) if subject_count else 0
    overall_grade = get_letter_grade(overall_average)

    context = {
        'student': student,
        'subject_scores': subject_scores,
        'overall_average': overall_average,
        'overall_grade': overall_grade,
    }
    return render(request, 'reports/report_card.html', context)


@login_required
def generate_report_card_pdf(request, student_id):
    """Generate and download official PDF report card"""
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    student = get_object_or_404(Student, id=student_id)
    scores = Score.objects.filter(student=student).select_related('subject')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFillColorRGB(0, 0.2, 0.4)
    p.rect(0, height - 110, width, 110, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(width / 2, height - 60, "ELITE INTERNATIONAL SCHOOL")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 95, "OFFICIAL REPORT CARD • 2025")

    # Student Info
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 16)
    y = height - 150
    p.drawString(50, y, f"Student: {student.user.get_full_name()}")
    p.drawString(50, y - 30, f"Roll No: {getattr(student, 'roll_number', 'N/A')}")
    p.drawString(50, y - 60, f"Class: {student.classroom} | Section: {student.section}")
    p.drawString(50, y - 90, f"Generated: {timezone.now().strftime('%d %B %Y')}")

    # Table Data
    data = [['Subject', 'Exam Type', 'Marks', 'Grade']]
    for s in scores:
        data.append([
            s.subject.name,
            s.get_exam_type_display(),
            str(s.score),
            s.grade or '-'
        ])

    if len(data) == 1:
        data.append(['-', 'No scores recorded', '-', '-'])

    # Table
    table = Table(data, colWidths=[180, 130, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f8ff')]),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 600)

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"{getattr(student, 'roll_number', 'student')}_Report_Card_2025.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def get_letter_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 96: return 'A'
    elif score >= 90: return 'A-'
    elif score >= 85: return 'B+'
    elif score >= 80: return 'B'
    elif score >= 75: return 'B-'
    elif score >= 70: return 'C+'
    elif score >= 65: return 'C'
    elif score >= 60: return 'C-'
    elif score >= 50: return 'D'
    else: return 'F'

# @login_required
# def generate_id_card(request, student_id):
#     if not request.user.is_staff:
#         messages.error(request, "Access denied!")
#         return redirect('staff_dashboard')
    
#     student = get_object_or_404(Student, id=student_id)
#     context = {'student': student}
#     return render(request, 'reports/id_card.html', context)  # create this template later

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from users.models import CustomUser
import qrcode
from io import BytesIO
from base64 import b64encode
from django.utils import timezone

@login_required
def id_card(request, user_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if user.role not in ['student', 'teacher']:
        messages.error(request, "ID card only for students and teachers.")
        return redirect('staff_dashboard')

    # Generate real QR code (scan will give user.id|role)
    qr_data = f"{user.id}|{user.role}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 so we can show it in HTML
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'user': user,
        'qr_base64': qr_base64,
        'today': timezone.now().date(),
    }

    return render(request, 'reports/id_card.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import time

@login_required
def qr_scan(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    context = {
        'current_time': timezone.now(),
    }
    return render(request, 'reports/qr_scan.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from django.utils import timezone

@csrf_exempt  # temporary for testing
@login_required
def qr_scan_process(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff only'}, status=403)

    try:
        import json
        data = json.loads(request.body)
        input_data = data.get('qr_data', '').strip()
    except:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    if not input_data:
        return JsonResponse({'error': 'No data'}, status=400)

    user = None

    # Case 1: QR format "user_id|role"
    if '|' in input_data:
        try:
            user_id, role = input_data.split('|')
            user_id = int(user_id)
            user = CustomUser.objects.select_related('student_profile', 'teacher_profile').get(id=user_id, role=role)
        except:
            pass

    # Case 2: Manual entry — roll number or employee ID
    if not user:
        # Try student roll_number
        try:
            user = CustomUser.objects.select_related('student_profile').get(
                role='student',
                student_profile__roll_number=input_data
            )
        except CustomUser.DoesNotExist:
            pass

        # Try teacher employee_id
        if not user:
            try:
                user = CustomUser.objects.select_related('teacher_profile').get(
                    role='teacher',
                    teacher_profile__employee_id=input_data
                )
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

    # Get info
    photo_url = user.photo.url if user.photo else None
    current_time = timezone.now().strftime('%H:%M')
    current_date = timezone.now().strftime('%d %B %Y')

    return JsonResponse({
        'name': user.get_full_name(),
        'photo': photo_url,
        'role': user.get_role_display(),
        'roll_number': (
            user.student_profile.roll_number if user.role == 'student' else
            user.teacher_profile.employee_id if user.role == 'teacher' else user.id
        ),
        'date': current_date,
        'time': current_time,
        'status': 'Present',
        'status_class': 'present',
        'message': f"Welcome {user.first_name}! Marked at {current_time} on {current_date}",
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .models import Notification, NotificationRead
from core.models import ClassRoom
from users.models import CustomUser

def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required, login_url='home')  # or any redirect
def send_notification(request):
    classrooms = ClassRoom.objects.all()
    students = CustomUser.objects.filter(role='student').select_related('student_profile')
    teachers = CustomUser.objects.filter(role='teacher')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        recipient_type = request.POST.get('recipient_type')

        if not title or not message:
            messages.error(request, "Title and message are required.")
        elif recipient_type not in dict(Notification.RECIPIENT_CHOICES):
            messages.error(request, "Invalid recipient type.")
        else:
            with transaction.atomic():
                notification = Notification.objects.create(
                    title=title,
                    message=message,
                    recipient_type=recipient_type,
                    sender=request.user,
                )

                # Handle specific targets
                if recipient_type == 'class':
                    class_id = request.POST.get('classroom')
                    if class_id:
                        notification.specific_class = get_object_or_404(ClassRoom, id=class_id)
                        notification.save()
                elif recipient_type == 'individual':
                    user_id = request.POST.get('user')
                    if user_id:
                        notification.specific_user = get_object_or_404(CustomUser, id=user_id)
                        notification.save()

                # Create NotificationRead entries for all recipients
                recipients = notification.get_recipients()
                read_entries = [
                    NotificationRead(notification=notification, user=user)
                    for user in recipients
                ]
                NotificationRead.objects.bulk_create(read_entries)

            messages.success(request, f"Notification '{title}' sent successfully!")
            return redirect('send_notification')

    context = {
        'classrooms': classrooms,
        'students': students,
        'teachers': teachers,
        'recipient_choices': Notification.RECIPIENT_CHOICES,
    }
    return render(request, 'notification/send_notification.html', context)


# Optional: View sent notifications history
@login_required
@user_passes_test(staff_required)
def notification_history(request):
    notifications = Notification.objects.select_related(
        'sender', 'specific_class', 'specific_user'
    ).all()
    return render(request, 'notification/history.html', {'notifications': notifications})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification, NotificationRead

User = get_user_model()

@login_required
def my_notifications(request):
    """
    Display notifications for the current logged-in user based on role and recipient targeting.
    Works perfectly with your current Notification model (recipient_type + specific_class/user).
    """
    user = request.user
    role = None
    template = None

    # Base queryset: all NotificationRead entries for this user
    # This ensures we only show notifications that were explicitly delivered to them
    reads = NotificationRead.objects.filter(user=user).select_related(
        'notification__sender',
        'notification__specific_class'
    ).order_by('-notification__created_at')

    # Determine user role for template selection
    if hasattr(user, 'student'):
        role = 'student'
        template = 'notification/student_notifications.html'

    elif hasattr(user, 'teacher'):
        role = 'teacher'
        print('teacher')
        template = 'notification/teacher_notifications.html'

    elif hasattr(user, 'parent'):
        role = 'parent'
        template = 'notification/parent_notifications.html'

    else:
        # Admin or unknown role — still show notifications sent to them
        role = 'user'
        template = 'notification/student_notifications.html'  # Reuse student template or make generic

    # If no template found or no access, fallback
    if template is None:
        return render(request, 'notification/no_access.html', {
            'message': 'Notification access not configured for your role.'
        })

    # Calculate unread count
    unread_count = reads.filter(is_read=False).count()

    context = {
        'notifications': reads,        # This contains NotificationRead objects
        'unread_count': unread_count,
        'role': role,
    }

    return render(request, template, context)



@login_required
def teacher_notifications(request):
    """
    Display notifications for the current logged-in user based on role and recipient targeting.
    Works perfectly with your current Notification model (recipient_type + specific_class/user).
    """
    user = request.user
    role = None
    template = None

    # Base queryset: all NotificationRead entries for this user
    # This ensures we only show notifications that were explicitly delivered to them
    reads = NotificationRead.objects.filter(user=user).select_related(
        'notification__sender',
        'notification__specific_class'
    ).order_by('-notification__created_at')

    # Calculate unread count
    unread_count = reads.filter(is_read=False).count()

    context = {
        'notifications': reads,        # This contains NotificationRead objects
        'unread_count': unread_count,
        'role': role,
    }

    return render(request, 'notification/teacher_notifications.html', context)

@login_required
@csrf_exempt  # We'll use CSRF token in fetch
def mark_notification_read(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notif_id = data.get('notification_id')
            read_entry = NotificationRead.objects.get(
                notification_id=notif_id,
                user=request.user
            )
            read_entry.is_read = True
            read_entry.read_at = timezone.now()
            read_entry.save()
            return JsonResponse({'success': True})
        except NotificationRead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# views.py


from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import NotificationRead

@login_required
def mark_notification_read_all(request, pk):
    read_entry = NotificationRead.objects.filter(pk=pk, user=request.user).first()
    if read_entry and not read_entry.is_read:
        read_entry.is_read = True
        read_entry.read_at = timezone.now()
        read_entry.save()
        messages.success(request, "Notification marked as read.")
    return redirect('my_notifications')

from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import NotificationRead

@login_required
def mark_all_notifications_read(request):
    """
    Mark ALL unread notifications as read for the current user
    """
    # Update all unread NotificationRead entries for this user
    updated_count = NotificationRead.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )

    if updated_count > 0:
        messages.success(request, f"{updated_count} notification(s) marked as read!")
    else:
        messages.info(request, "No unread notifications to mark.")

    return redirect('my_notifications')  # Redirect back to notifications page

# from django.contrib.auth.decorators import login_required  # <-- comment out

from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from timetable.models import TimetableEntry
from core.models import Subject
from core.models import Student
from chat.models import Message
from reports.models import NotificationRead
from users.models import CustomUser
from timetable.models import Period,Day
def teacher_dashboard(request):
    teacher_user = request.user
    today = timezone.now().date()
    weekday = today.strftime('%A').lower()  # e.g., 'saturday'
    today_classes = TimetableEntry.objects.filter(
        teacher=teacher_user,
        day__name__iexact=weekday
    )
    pending_scores = Subject.objects.filter(
        timetable_entries__teacher=teacher_user
    ).distinct().annotate(
        score_count=Count('scores')
    ).filter(score_count=0)

    # Low attendance students
    low_attendance_students = Student.objects.filter(
        classroom__timetable_entries__teacher=teacher_user
    ).annotate(
        absences=Count('attendances', filter=Q(attendances__status='absent'))
    ).filter(absences__gt=2).select_related('user')

    # Unread counts
    unread_messages = Message.objects.filter(
        chat_room__participants=teacher_user,
        is_read=False
    ).exclude(sender=teacher_user).count()

    unread_notifications = NotificationRead.objects.filter(
        user=teacher_user,
        is_read=False
    ).count()

    context = {
        'teacher_name': teacher_user.get_full_name(),
        'today_classes': today_classes,
        'pending_scores_count': pending_scores.count(),
        'pending_scores': pending_scores[:5],
        'low_attendance_count': low_attendance_students.count(),
        'low_attendance_students': low_attendance_students[:5],
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
        'today': today,
        'weekday': today.strftime('%A'),
        'debug_weekday': weekday,
        'debug_entries': TimetableEntry.objects.filter(teacher=teacher_user).count(),
    }

    return render(request, 'teacher/dashboard.html', context)


from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from timetable.models import TimetableEntry, Day, Period
from core.models import Student
from chat.models import Message
from reports.models import NotificationRead
from users.models import CustomUser

def teacher_timetable(request):
    # DEVELOPMENT MODE — NO LOGIN
    teacher_user = request.user
    periods = Period.objects.all().order_by('number')
    days = Day.objects.all().order_by('id')  # <-- show all days, including Sunday

    entries = TimetableEntry.objects.filter(
        teacher=teacher_user
    ).select_related('classroom', 'subject', 'day', 'period')

    # Use day.name as string key — template can handle string
    grid = {}
    for day in days:
        grid[day.name] = {}  # 'monday', 'saturday', etc.
        for period in periods:
            grid[day.name][period] = None

    for entry in entries:
        day_key = entry.day.name  # 'saturday'
        if day_key in grid and entry.period in grid[day_key]:
            grid[day_key][entry.period] = entry

    context = {
        'periods': periods,
        'days': days,
        'grid': grid,
    }
    
    return render(request, 'teacher/timetable.html', context)


def teacher_subjects(request):
    teacher_user = request.user
    subjects = Subject.objects.filter(
        timetable_entries__teacher=teacher_user
    ).distinct().annotate(
        class_count=Count('timetable_entries__classroom', distinct=True),
        student_count=Count('timetable_entries__classroom__students', distinct=True),
        average_score=Avg('scores__score')  # <-- FIXED: 'score' not 'mark'
    ).order_by('name')

    context = {
        'subjects': subjects,
    }

    return render(request, 'teacher/subjects.html', context)


from django.shortcuts import render
from timetable.models import TimetableEntry

def my_classes(request):
    teacher_user = request.user
    entries = TimetableEntry.objects.filter(
        teacher=teacher_user
    ).select_related('classroom', 'subject', 'day', 'period').order_by('day__id', 'period__number')

    # Group by classroom
    classes = {}
    for entry in entries:
        classroom = entry.classroom
        if classroom not in classes:
            classes[classroom] = {
                'classroom': classroom,
                'subjects': [],
                'student_count': classroom.students.count(),  # <-- COMMENT THIS LINE
                # 'student_count': 0,  # temporary placeholder
            }
        classes[classroom]['subjects'].append({
            'subject': entry.subject,
            'day': entry.day.get_name_display(),
            'period_number': entry.period.number,
            'time': f"{entry.period.start_time} - {entry.period.end_time}",
        })

    context = {
        'classes': classes.values(),
    }

    return render(request, 'teacher/my_classes.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count

from timetable.models import TimetableEntry
from core.models import Student, Attendance, Score  # Score from core

@login_required
def manual_attendance(request):
    if request.user.role != 'teacher' and not request.user.is_staff:
        messages.error(request, "Access denied! Teachers only.")
        return redirect('teacher_dashboard')

    # Get teacher's timetable entries (to choose class/subject)
    timetable_entries = TimetableEntry.objects.filter(
        teacher=request.user
    ).select_related('classroom', 'subject', 'period', 'day').distinct()

    selected_entry = None
    students = []
    attendance_date = timezone.now().date()

    if request.method == 'POST':
        entry_id = request.POST.get('timetable_entry')
        try:
            selected_entry = TimetableEntry.objects.get(id=entry_id, teacher=request.user)
        except TimetableEntry.DoesNotExist:
            messages.error(request, "Invalid class selection.")
            return redirect('teacher_attendance_manual')

        # Save attendance for each student
        for student in selected_entry.classroom.students.all():
            status = 'present' if request.POST.get(f'student_{student.id}') else 'absent'

            Attendance.objects.update_or_create(
                student=student,
                subject=selected_entry.subject,
                date=attendance_date,
                defaults={
                    'status': status,
                    'marked_by': request.user
                }
            )

            # Auto penalty system
            absences = Attendance.objects.filter(
                student=student,
                subject=selected_entry.subject,
                status='absent'
            ).count()

            # Get or create score (use 'attendance' as exam_type to avoid conflict)
            score_obj, created = Score.objects.get_or_create(
                student=student,
                subject=selected_entry.subject,
                exam_type='attendance',  # special type for attendance penalty
                defaults={
                    'score': 100.00,
                    'grade': 'A'
                }
            )

            # Apply penalty
            if absences >= 3:
                score_obj.score = 0.00
                score_obj.grade = 'F'
            elif absences == 2:
                score_obj.score = max(0.00, score_obj.score - 10)
            elif absences == 1:
                score_obj.score = max(0.00, score_obj.score - 5)

            score_obj.save()

        messages.success(request, f"Attendance saved for {selected_entry.classroom.name} - {selected_entry.subject.name}")
        return redirect('teacher_attendance_manual')

    # Show form — select class
    if request.GET.get('timetable_entry'):
        entry_id = request.GET.get('timetable_entry')
        try:
            selected_entry = TimetableEntry.objects.get(id=entry_id, teacher=request.user)
            students = selected_entry.classroom.students.all().order_by('roll_number')
        except TimetableEntry.DoesNotExist:
            messages.error(request, "Invalid class selection.")

    context = {
        'timetable_entries': timetable_entries,
        'selected_entry': selected_entry,
        'students': students,
        'attendance_date': attendance_date,
    }

    return render(request, 'teacher/manual_attendance.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import qrcode
from io import BytesIO
import base64

from timetable.models import TimetableEntry
from core.models import Attendance

@login_required
def qr_attendance(request):
    if request.user.role != 'teacher' and not request.user.is_staff:
        messages.error(request, "Access denied!")
        return redirect('teacher_dashboard')

    timetable_entries = TimetableEntry.objects.filter(
        teacher=request.user,
        day__name__iexact=timezone.now().strftime('%A').lower()
    ).select_related('classroom', 'subject', 'period')

    selected_entry = None
    qr_code = None
    token = None

    if request.method == 'POST':
        entry_id = request.POST.get('timetable_entry')
        selected_entry = get_object_or_404(TimetableEntry, id=entry_id, teacher=request.user)

        # Generate token (simple — entry ID + date)
        token = f"{selected_entry.id}-{timezone.now().date()}"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        LOCAL_IP = "172.20.10.3"
        qr.add_data(f"http://{LOCAL_IP}:8000/qr-scan/?token={token}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'timetable_entries': timetable_entries,
        'selected_entry': selected_entry,
        'qr_code': qr_code,
        'token': token,
    }

    return render(request, 'teacher/qr_attendance.html', context)

# def qr_scan(request):
#     token = request.GET.get('token')
#     if not token:
#         return render(request, 'teacher/qr_scan.html', {'error': 'Invalid QR'})

#     # Parse token (simple format: entry_id-date)
#     try:
#         entry_id, date_str = token.split('-')
#         entry = TimetableEntry.objects.get(id=entry_id)
#         scan_date = timezone.now().date()
#         if str(scan_date) != date_str:
#             return render(request, 'teacher/qr_scan.html', {'error': 'QR expired'})
#     except:
#         return render(request, 'teacher/qr_scan.html', {'error': 'Invalid QR'})

#     # Mark attendance (assume student is logged in — or use device ID later)
#     student = request.user.student_profile  # if student logged in

#     Attendance.objects.update_or_create(
#         student=student,
#         subject=entry.subject,
#         date=scan_date,
#         defaults={'status': 'present', 'marked_by': entry.teacher.user}
#     )

#     return render(request, 'teacher/qr_scan.html', {
#         'success': True,
#         'classroom': entry.classroom.name,
#         'subject': entry.subject.name,
#     })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from timetable.models import TimetableEntry
from core.models import Student
from core.models import Score

def teacher_enter_scores(request):
    teacher_user = request.user
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher_user
    ).select_related('classroom', 'subject', 'period', 'day').distinct()

    selected_entry = None
    students = []
    exam_type = request.GET.get('exam_type', 'midterm')

    # Select class
    if request.GET.get('timetable_entry'):
        entry_id = request.GET.get('timetable_entry')
        try:
            selected_entry = TimetableEntry.objects.get(id=entry_id, teacher=teacher_user)
            students = selected_entry.classroom.students.all().order_by('roll_number')
        except TimetableEntry.DoesNotExist:
            messages.error(request, "Invalid class selection.")

    # Save scores (when form submitted)
    if request.method == 'POST':
        entry_id = request.POST.get('timetable_entry')
        try:
            selected_entry = TimetableEntry.objects.get(id=entry_id, teacher=teacher_user)
        except TimetableEntry.DoesNotExist:
            messages.error(request, "Invalid class.")
            return redirect('teacher_enter_scores')

        for student in selected_entry.classroom.students.all():
            marks_key = f'marks_{student.id}'
            if marks_key in request.POST:
                marks = request.POST[marks_key]
                if marks:
                    Score.objects.update_or_create(
                        student=student,
                        subject=selected_entry.subject,
                        exam_type=exam_type,
                        defaults={
                            'score': marks,
                            'recorded_by': teacher_user
                        }
                    )

        messages.success(request, "Scores saved successfully!")
        return redirect('teacher_enter_scores')

    context = {
        'timetable_entries': timetable_entries,
        'selected_entry': selected_entry,
        'students': students,
        'exam_type': exam_type,
    }

    return render(request, 'teacher/enter_scores.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.models import Student, Score
from core.models import Subject

@login_required
def view_student_scores(request, student_id):
    if request.user.role != 'teacher' and not request.user.is_staff:
        messages.error(request, "Access denied! Teachers only.")
        return redirect('teacher_dashboard')

    # Get the student
    student = get_object_or_404(Student, id=student_id)

    # Get all scores for this student
    scores = Score.objects.filter(
        student=student
    ).select_related('subject').order_by('subject__name', 'exam_type')

    # Group by subject
    scores_by_subject = {}
    for score in scores:
        subject = score.subject
        if subject not in scores_by_subject:
            scores_by_subject[subject] = []
        scores_by_subject[subject].append(score)

    context = {
        'student': student,
        'scores_by_subject': scores_by_subject,
    }

    return render(request, 'teacher/view_student_scores.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from users.models import CustomUser
from core.models import Student, Parent, Profile
from timetable.models import TimetableEntry
from core.models import ClassRoom

@login_required
def my_profile(request):
    user = request.user

    # Base profile data
    profile_data = {
        'user': user,
        'photo': '/static/images/default-avatar.png',
        'join_date': user.date_joined.date(),
        'phone': user.phone or 'Not set',
    }

    # Real profile photo
    if hasattr(user, 'profile') and user.profile.photo:
        profile_data['photo'] = user.profile.photo.url

    # Role-specific data
    if user.role == 'teacher':
        # Get unique classrooms
        teacher_classes = TimetableEntry.objects.filter(
            teacher=user
        ).values('classroom').distinct()

        profile_data['classes'] = ClassRoom.objects.filter(
            id__in=teacher_classes
        )

        profile_data['total_students'] = Student.objects.filter(
            classroom__in=teacher_classes
        ).distinct().count()

    elif user.role == 'student':
        try:
            student = Student.objects.get(user=user)
            profile_data['student'] = student
            profile_data['classroom'] = student.classroom
        except Student.DoesNotExist:
            profile_data['student'] = None

    elif user.role == 'parent':
        try:
            parent = Parent.objects.get(user=user)
            profile_data['children'] = parent.children.all()
        except Parent.DoesNotExist:
            profile_data['children'] = None

    elif user.is_staff or user.is_superuser:
        profile_data['total_users'] = CustomUser.objects.count()
        profile_data['total_classes'] = ClassRoom.objects.count()

    # Update profile
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)

        if 'photo' in request.FILES:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.photo = request.FILES['photo']
            profile.save()

        user.save()
        messages.success(request, "Profile updated successfully!")

    context = {
        'profile_data': profile_data,
    }

    return render(request, 'teacher/my_profile.html', context)

