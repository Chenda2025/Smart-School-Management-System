# users/views.py — ELITE FIXED VERSION 2025 — 100% WORKING WITH CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser
from core.models import Student, Teacher, Parent  # if you use related profiles later

# ─────────────────────────────────────
# ALL USERS LIST — STAFF & ADMIN ONLY
# ─────────────────────────────────────
@login_required
def all_users_list(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied! Staff only.")
        return redirect('staff_dashboard')

    query = request.GET.get('q', '').strip()
    selected_role = request.GET.get('role', '')

    users = CustomUser.objects.all().order_by('role', 'first_name', 'last_name')

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    if selected_role:
        users = users.filter(role=selected_role)

    # Stats for your epic dashboard
    admin_count = CustomUser.objects.filter(role='admin').count()
    teacher_count = CustomUser.objects.filter(role='teacher').count()
    student_count = CustomUser.objects.filter(role='student').count()
    parent_count = CustomUser.objects.filter(role='parent').count()

    context = {
        'users': users,
        'query': query,
        'selected_role': selected_role,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'parent_count': parent_count,
    }
    return render(request, 'users/all_users.html', context)


# ─────────────────────────────────────
# USER PROFILE — VIEW ANY PROFILE
# ─────────────────────────────────────
@login_required
def user_profile(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk)
    context = {'profile_user': profile_user}
    return render(request, 'users/user_profile.html', context)


# ─────────────────────────────────────
# ADD USER — STAFF & ADMIN ONLY
# ─────────────────────────────────────
@login_required
def add_user(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied! Only staff can add users.")
        return redirect('staff_dashboard')

    if request.method == 'POST':
        # Extract data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'student')
        is_staff = 'is_staff' in request.POST
        photo = request.FILES.get('photo')

        # Validation
        errors = False

        if not all([first_name, last_name, username, password1, password2]):
            messages.error(request, "All required fields must be filled.")
            errors = True

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            errors = True

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            errors = True

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            errors = True

        if errors:
            return render(request, 'users/add_user.html')

        # Create user
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email or '',
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone or '',
                is_staff=is_staff,
            )
            if photo:
                user.photo = photo
                user.save()

            messages.success(request, f"User '{user.get_full_name() or user.username}' created successfully!")
            return redirect('all_users_list')

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")

    return render(request, 'users/add_user.html')


# ─────────────────────────────────────
# EDIT PROFILE — OWN OR STAFF CAN EDIT ANY
# ─────────────────────────────────────
@login_required
def edit_profile(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk)

    # Permission check
    if not request.user.is_staff and request.user != profile_user:
        messages.error(request, "You can only edit your own profile!")
        return redirect('user_profile', pk=pk)

    if request.method == 'POST':
        # Get data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        new_password = request.POST.get('password')  # optional
        role = request.POST.get('role', profile_user.role)
        is_staff_check = 'is_staff' in request.POST
        photo = request.FILES.get('photo')

        # Update basic fields
        profile_user.first_name = first_name
        profile_user.last_name = last_name
        profile_user.email = email

        # Only staff can change role & is_staff
        if request.user.is_staff:
            profile_user.role = role
            profile_user.is_staff = is_staff_check

        # Change password if provided
        if new_password:
            profile_user.set_password(new_password)
        
        # Update photo if uploaded
        if photo:
            profile_user.photo = photo

        profile_user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile', pk=profile_user.id)

    context = {
        'profile_user': profile_user,
    }
    return render(request, 'users/edit_profile.html', context)

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Role-based redirect
            if user.is_staff or user.role == 'admin':
                return redirect('staff_dashboard')
            elif user.role == 'teacher':
                return redirect('teacher_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('staff_dashboard')  # fallback
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'core/login.html')