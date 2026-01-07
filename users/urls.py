# users/urls.py — UPDATED TO MATCH YOUR TEMPLATE LINKS
from django.urls import path
from . import views

urlpatterns = [
    # All Users List
    path('all/', views.all_users_list, name='all_users_list'),
    
    # Add User
    path('add/', views.add_user, name='add_user'),
    
    # User Profile View (e.g., /profile/5/)
    path('profile/<int:pk>/', views.user_profile, name='user_profile'),
    
    # Edit Profile (e.g., /profile/5/edit/)
    path('profile/<int:pk>/edit/', views.edit_profile, name='edit_profile'),
]