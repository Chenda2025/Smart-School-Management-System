from django.urls import path
from .views import(
    chat_list,
    start_chat, 
    send_message, 
    chat_room,

)
app_name = 'chat'

urlpatterns = [
    ## chat for admin and staff
    path('',chat_list, name='chat_list'),
    path('start/<int:user_id>/', start_chat, name='start_chat'),
    path('send/', send_message, name='send_message'),
    path('room/<int:room_id>/', chat_room, name='chat_room'),

   
]

