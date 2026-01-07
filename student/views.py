from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max
from django.utils import timezone
from datetime import timedelta
import random

from core.models import Student, Attendance, Score, Subject
from timetable.models import TimetableEntry, Period


# Motivational quotes list (outside the view for efficiency)
MOTIVATIONAL_QUOTES = [
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"quote": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"quote": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"quote": "You are never too old to set another goal or to dream a new dream.", "author": "C.S. Lewis"},
    {"quote": "The harder you work for something, the greater you’ll feel when you achieve it.", "author": "Unknown"},
    {"quote": "Dream it. Wish it. Do it.", "author": "Unknown"},
    {"quote": "Great things never come from comfort zones.", "author": "Unknown"},
    {"quote": "Wake up with determination. Go to bed with satisfaction.", "author": "Unknown"},
    {"quote": "Little things make big days.", "author": "Unknown"},
]


@login_required
def student_dashboard(request):
    try:
        student = request.user.student_profile
    except AttributeError:
        return render(request, 'error.html', {'message': 'No student profile found'})

    today = timezone.now().date()
    month_start = today - timedelta(days=today.day - 1)

    # Random motivational quote
    motivational_quote = random.choice(MOTIVATIONAL_QUOTES)

    # 1. Overall average & letter grade
    overall_avg = Score.objects.filter(student=student).aggregate(avg=Avg('score'))['avg'] or 0
    overall_average = round(overall_avg, 1)

    if overall_average >= 96:
        overall_grade = 'A'
    elif overall_average >= 90:
        overall_grade = 'A-'
    elif overall_average >= 85:
        overall_grade = 'B+'
    elif overall_average >= 80:
        overall_grade = 'B'
    elif overall_average >= 75:
        overall_grade = 'B-'
    elif overall_average >= 70:
        overall_grade = 'C+'
    elif overall_average >= 65:
        overall_grade = 'C'
    elif overall_average >= 60:
        overall_grade = 'C-'
    elif overall_average >= 50:
        overall_grade = 'D'
    else:
        overall_grade = 'F'

    # 2. Attendance this month
    attendances_this_month = Attendance.objects.filter(
        student=student,
        date__gte=month_start,
        date__lte=today
    )
    total_days = attendances_this_month.count()
    present_days = attendances_this_month.filter(status='present').count()
    absent_days = attendances_this_month.filter(status='absent').count()
    attendance_percentage = round(present_days / total_days * 100, 1) if total_days > 0 else 0

    # 3. Attendance calendar
    attendance_calendar = []
    day = month_start
    while day <= today:
        day_record = attendances_this_month.filter(date=day).first()
        status = day_record.status if day_record else None
        attendance_calendar.append({
            'date': day,
            'present': status == 'present',
            'absent': status == 'absent',
        })
        day += timedelta(days=1)

    # 4. Placeholders
    unread_messages = 0
    next_exam = None

    # 5. Subject grades
    subjects = Subject.objects.filter(classroom=student.classroom)
    subject_grades = []
    for subj in subjects:
        subj_scores = Score.objects.filter(student=student, subject=subj)
        subj_avg = subj_scores.aggregate(avg=Avg('score'))['avg'] or 0
        subj_average = round(subj_avg, 1)

        # Letter grade
        if subj_average >= 96: subj_grade = 'A'
        elif subj_average >= 90: subj_grade = 'A-'
        elif subj_average >= 85: subj_grade = 'B+'
        elif subj_average >= 80: subj_grade = 'B'
        elif subj_average >= 75: subj_grade = 'B-'
        elif subj_average >= 70: subj_grade = 'C+'
        elif subj_average >= 65: subj_grade = 'C'
        elif subj_average >= 60: subj_grade = 'C-'
        elif subj_average >= 50: subj_grade = 'D'
        else: subj_grade = 'F'

        latest_score = subj_scores.order_by('-recorded_at').first()
        subject_grades.append({
            'subject': subj,
            'average': subj_average,
            'letter_grade': subj_grade,
            'latest_score': latest_score.score if latest_score else None,
        })

    # 6. Class rank
    class_students = Student.objects.filter(classroom=student.classroom)
    ranked = class_students.annotate(avg_score=Avg('scores__score')).order_by('-avg_score')
    student_rank = list(ranked).index(student) + 1 if student in ranked else "-"

    # 7. Performance chart data
    chart_labels = []
    chart_my_scores = []
    chart_class_averages = []
    has_data = False

    student_exams = Score.objects.filter(student=student) \
        .values('exam_type') \
        .annotate(latest_date=Max('recorded_at')) \
        .order_by('-latest_date')[:8]

    class_student_ids = Student.objects.filter(classroom=student.classroom).values_list('id', flat=True)

    for exam in student_exams:
        exam_type = exam['exam_type']
        my_score_obj = Score.objects.filter(
            student=student,
            exam_type=exam_type
        ).order_by('-recorded_at').first()

        if my_score_obj:
            has_data = True
            chart_labels.append(exam_type)
            chart_my_scores.append(round(my_score_obj.score, 1))

            class_avg = Score.objects.filter(
                student_id__in=class_student_ids,
                exam_type=exam_type
            ).aggregate(avg=Avg('score'))['avg']
            chart_class_averages.append(round(class_avg or 0, 1))

    if not has_data:
        chart_labels = ['No exams recorded yet']
        chart_my_scores = [0]
        chart_class_averages = [0]
    print(chart_labels, chart_my_scores, chart_class_averages, has_data)


    # 8. Timetable
    timetable = []
    try:
        periods = Period.objects.all().order_by('start_time')
        today_weekday = today.strftime("%A")

        for period in periods:
            entries = TimetableEntry.objects.filter(
                classroom=student.classroom,
                period=period
            ).select_related('subject', 'teacher')

            schedule_dict = {}
            for entry in entries:
                day_name = entry.day.name.strip().title()
                schedule_dict[day_name] = entry

            timetable.append({
                'period': period,
                'schedule': schedule_dict,
                'is_today_day': today_weekday,
            })
    except Exception as e:
        print(f"Timetable loading error: {e}")
        timetable = []

    # === FINAL CONTEXT (created once at the end) ===
    context = {
        'student': student,
        'overall_average': overall_average,
        'overall_grade': overall_grade,
        'attendance_percentage': attendance_percentage,
        'present_days': present_days,
        'absent_days': absent_days,
        'total_days': total_days,
        'unread_messages': unread_messages,
        'next_exam': next_exam,
        'subject_grades': subject_grades,
        'attendance_calendar': attendance_calendar,
        'timetable': timetable,
        'student_rank': student_rank,
        'today': today,
        'motivational_quote': motivational_quote,

        # Chart data
        'chart_labels': chart_labels,
        'chart_my_scores': chart_my_scores,
        'chart_class_averages': chart_class_averages,
        'chart_has_data': has_data,
    }

    return render(request, 'student/dashboard.html', context)

# student/views.py

@login_required
def my_report_card(request):
    """Student can view their own report card"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, "No student profile found.")
        return redirect('student_dashboard')

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

        score_values = [float(s.score) for s in [midterm, final, quiz, assignment] if s]
        avg = sum(score_values) / len(score_values) if score_values else 0
        avg = round(avg, 1)

        subject_scores.append({
            'subject': subject,
            'midterm': midterm.score if midterm else '-',
            'final': final.score if final else '-',
            'quiz': quiz.score if quiz else '-',
            'assignment': assignment.score if assignment else '-',
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
        'today': timezone.now().date(),
    }

    return render(request, 'student/my_report_card.html', context)

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

# student/views.py
# student/views.py — ADD THIS LINE AT THE TOP
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from core.models import Student
@login_required
def my_id_card(request, student_id):
    if not request.user.is_student or request.user.student_profile.id != student_id:
        messages.error(request, "Access denied!")
        return redirect('student_dashboard')

    student = get_object_or_404(Student, id=student_id)
    context = {'student': student}
    return render(request, 'student/my_id_card.html', context)

# student/views.py or core/views.py
@login_required
def my_attendance(request):
    if not request.user.is_student:
        messages.error(request, "Access denied!")
        return redirect('staff_dashboard')

    student = request.user.student_profile

    # Current month
    today = timezone.now().date()
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # All attendance this month
    attendance_records = Attendance.objects.filter(
        student=student,
        date__gte=month_start,
        date__lte=month_end
    )

    # Stats
    present_count = attendance_records.filter(status='present').count()
    absent_count = attendance_records.filter(status='absent').count()
    late_count = attendance_records.filter(status='late').count()
    total = present_count + absent_count + late_count
    attendance_percentage = round(present_count / total * 100, 1) if total > 0 else 0

    # Calendar days
    calendar_days = []
    current = month_start
    while current <= month_end:
        record = attendance_records.filter(date=current).first()
        status = ''
        if record:
            status = record.status
        calendar_days.append({
            'number': current.day,
            'weekday': current.strftime('%a'),
            'status': status,
            'is_today': current == today,
        })
        current += timedelta(days=1)

    # Subject breakdown
    subjects = Subject.objects.filter(classroom=student.classroom)
    subject_attendance = []
    for subject in subjects:
        records = attendance_records.filter(subject=subject)
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        late = records.filter(status='late').count()
        total = present + absent + late
        percentage = round(present / total * 100, 1) if total > 0 else 0
        subject_attendance.append({
            'name': subject.name,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': percentage,
        })

    context = {
        'student': student,
        'current_month': month_start,
        'attendance_percentage': attendance_percentage,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'calendar_days': calendar_days,
        'subject_attendance': subject_attendance,
    }
    return render(request, 'student/my_attendance.html', context)

# student/views.py or core/views.py — FINAL MY TIMETABLE VIEW
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from timetable.models import TimetableEntry, Period, Day
from core.models import Student

@login_required
def my_timetable(request):
    if not request.user.is_student:
        messages.error(request, "Access denied!")
        return redirect('staff_dashboard')

    student = request.user.student_profile
    today = timezone.now().date()
    weekday = today.weekday()  # 0 = Monday

    # Calculate current week
    week_start = today - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)

    # Get all timetable entries for this classroom
    entries = TimetableEntry.objects.filter(
        classroom=student.classroom
    ).select_related('subject', 'teacher', 'period', 'day')

    # Get all periods to ensure every time slot is shown
    periods = Period.objects.all().order_by('number')

    # Build timetable grid
    timetable = []
    for period in periods:
        period_entry = {
            'time': f"{period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}",
            'monday': None,
            'tuesday': None,
            'wednesday': None,
            'thursday': None,
            'friday': None,
        }

        # Fill with actual entries
        for entry in entries.filter(period=period):
            day_name = entry.day.name
            period_entry[day_name] = entry

            # Mark today
            if entry.day.name == ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'][weekday]:
                period_entry[day_name].is_today = True

        timetable.append(period_entry)

    context = {
        'student': student,
        'timetable': timetable,
        'today': today,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'student/my_timetable.html', context)
# student/views.py — FINAL STUDENT CHAT VIEWS — FULLY WORKING 2025


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.models import CustomUser  # Adjust if CustomUser is elsewhere
from chat.models import ChatRoom, Message
@login_required
def chat_list_student(request):
    user = request.user
    # Get all chat rooms the user is in, sorted by latest activity
    chat_rooms = ChatRoom.objects.filter(participants=user).order_by('-last_message_at', '-created_at')

    rooms_with_info = []
    for room in chat_rooms:
        # For 1-on-1 chats, get the other participant
        other_user = None
        if not room.is_group:
            other_user = room.participants.exclude(id=user.id).first()

        # Last message preview
        last_message = room.messages.select_related('sender').order_by('-timestamp').first()

        # Unread count (messages from others that are unread)
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()

        rooms_with_info.append({
            'room': room,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    # Users the student can start a chat with (teachers & admins only)
    available_users = CustomUser.objects.exclude(id=user.id)
    if user.role == 'student':
        available_users = available_users.filter(role__in=['teacher', 'admin'])

    context = {
        'rooms_with_info': rooms_with_info,
        'available_users': available_users.order_by('first_name'),
        'user': user,
    }
    return render(request, 'student/chat_list.html', context)


@login_required
def start_chat_student(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Restrict students to only chat with teachers/admins
    if request.user.role == 'student' and other_user.role not in ['teacher', 'admin']:
        messages.error(request, "Students can only chat with teachers or admins.")
        return redirect('chat:chat_list')

    # Correct way: Find existing 1-on-1 room with both users
    room = ChatRoom.objects.filter(
        Q(participants=request.user) & Q(participants=other_user),
        is_group=False
    ).first()

    if not room:
        room = ChatRoom.objects.create(is_group=False)
        room.participants.add(request.user, other_user)

    return redirect('student:chat_room', room_id=room.id)


@login_required
def send_message_student(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        content = request.POST.get('content', '').strip()

        if not room_id:
            messages.error(request, "Invalid room.")
            return redirect('chat:chat_list')

        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)

        if content:
            Message.objects.create(
                chat_room=room,
                sender=request.user,
                content=content
            )
            room.update_last_message()  # Assuming you have this method on ChatRoom
            messages.success(request, "Message sent!")

        return redirect('student:chat_room', room_id=room_id)

    return redirect('student:chat_list')


@login_required
def chat_room_student(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # Access control: user must be a participant
    if request.user not in room.participants.all():
        messages.error(request, "Access denied.")
        return redirect('chat:chat_list')

    # Get other user in 1-on-1 chat
    other_user = None
    if not room.is_group:
        other_user = room.participants.exclude(id=request.user.id).first()

    # Load messages
    messages = room.messages.select_related('sender').order_by('timestamp')

    # Mark unread messages from others as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    context = {
        'room': room,
        'other_user': other_user,
        'messages': messages,
        'user': request.user,
    }
    return render(request, 'student/chat_room.html', context)
# student/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Student  # Adjust if Student is in another app

@login_required
def my_profile(request):
    try:
        student = Student.objects.select_related(
            'user', 'classroom', 'section'
        ).get(user_id=request.user.id)
    except Student.DoesNotExist:
        messages.warning(request, "You are not registered as a student.")
        return render(request, 'student/my_profile_not_student.html')

    context = {
        'student': student,
    }
    return render(request, 'student/student_info.html', context)

