from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TimetableEntry, ClassRoom, Subject, Period, Day
from users.models import CustomUser

@login_required
def assign_timetable(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied!")
        return redirect('staff_dashboard')

    # For edit mode
    entry_id = request.GET.get('edit')
    entry_to_edit = None
    if entry_id:
        entry_to_edit = get_object_or_404(TimetableEntry, id=entry_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            delete_id = request.POST.get('entry_id')
            entry = get_object_or_404(TimetableEntry, id=delete_id)
            entry.delete()
            messages.success(request, "Schedule entry deleted successfully!")
            return redirect('assign_timetable')

        try:
            # Get objects from POST IDs
            classroom = ClassRoom.objects.get(id=request.POST.get('classroom'))
            subject = Subject.objects.get(id=request.POST.get('subject'))
            teacher = CustomUser.objects.get(id=request.POST.get('teacher'))
            day = Day.objects.get(id=request.POST.get('day'))
            period = Period.objects.get(id=request.POST.get('period'))

            # Check for conflict
            if action == 'update':
                entry_id = request.POST.get('entry_id')
                entry = get_object_or_404(TimetableEntry, id=entry_id)
                # Exclude current entry in conflict check
                conflict = TimetableEntry.objects.filter(
                    classroom=classroom,
                    day=day,
                    period=period
                ).exclude(id=entry.id).exists()
            else:
                conflict = TimetableEntry.objects.filter(
                    classroom=classroom,
                    day=day,
                    period=period
                ).exists()

            if conflict:
                messages.error(request, "Conflict: This class already has a lesson at this time.")
            else:
                if action == 'update':
                    entry.classroom = classroom
                    entry.subject = subject
                    entry.teacher = teacher
                    entry.day = day
                    entry.period = period
                    entry.save()
                    messages.success(request, "Schedule updated successfully!")
                else:
                    TimetableEntry.objects.create(
                        classroom=classroom,
                        subject=subject,
                        teacher=teacher,
                        day=day,
                        period=period,
                    )
                    messages.success(request, "Schedule assigned successfully!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}. Please try again.")

        return redirect('assign_timetable')

    context = {
        'classrooms': ClassRoom.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': CustomUser.objects.filter(role='teacher'),
        'days': Day.objects.all(),
        'periods': Period.objects.all(),
        'entries': TimetableEntry.objects.all().select_related(
            'classroom', 'subject', 'teacher', 'day', 'period'
        ).order_by('day__id', 'period__number'),
        'entry_to_edit': entry_to_edit,
    }
    return render(request, 'timetable/schedule.html', context)