from django.urls import path
from . import views
from reports.views import my_notifications,mark_notification_read

app_name = 'student'

urlpatterns = [
    path('', views.chat_list_student, name='chat_list_student'),
    path('start/<int:user_id>/', views.start_chat_student, name='start_chat_student'),
    path('room/<int:room_id>/', views.chat_room_student, name='chat_room'),
    path('send/', views.send_message_student, name='send_message'),
    path('my-profile/', views.my_profile, name='my_profile'),
   # Notifications
    path('notifications/', my_notifications, name='my_notifications'),  # Fixed name!
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),

]