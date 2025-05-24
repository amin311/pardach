from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Chat URLs
    path('chats/', views.ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<uuid:chat_id>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chats/<uuid:chat_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<uuid:message_id>/read/', views.MessageDetailView.as_view(), name='message-mark-read'),
    
    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<uuid:notification_id>/read/', views.NotificationMarkReadView.as_view(), name='notification-mark-read'),
]
