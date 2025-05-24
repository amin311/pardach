from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Chat, Message, Notification
from .serializers import ChatSerializer, MessageSerializer, NotificationSerializer
from drf_spectacular.utils import extend_schema

class ChatListCreateView(APIView):
    """API برای دریافت لیست و ایجاد چت‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست چت‌ها", responses={200: ChatSerializer(many=True)})
    def get(self, request):
        """دریافت لیست چت‌های کاربر"""
        try:
            # چت‌هایی که کاربر جاری در آنها شرکت دارد یا مربوط به کسب‌وکارهای اوست
            chats = Chat.objects.filter(
                Q(participants=request.user) | 
                Q(business__users__user=request.user)
            ).distinct()
            
            serializer = ChatSerializer(chats, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'خطا در دریافت چت‌ها: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="ایجاد چت جدید", request=ChatSerializer, responses={201: ChatSerializer})
    def post(self, request):
        """ایجاد چت جدید"""
        try:
            serializer = ChatSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                chat = serializer.save()
                # اضافه کردن خودکار کاربر جاری به شرکت‌کنندگان
                if 'participant_ids' not in request.data or not request.data['participant_ids']:
                    chat.participants.add(request.user)
                return Response(
                    ChatSerializer(chat, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'خطا در ایجاد چت: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChatDetailView(APIView):
    """API برای دریافت، به‌روزرسانی و حذف یک چت خاص"""
    permission_classes = [IsAuthenticated]

    def get_chat(self, chat_id, user):
        """دریافت چت با بررسی دسترسی"""
        try:
            chat = Chat.objects.get(id=chat_id)
            # بررسی دسترسی: کاربر باید شرکت‌کننده در چت یا عضو کسب‌وکار مرتبط باشد
            if not (chat.participants.filter(id=user.id).exists() or 
                   (chat.business and chat.business.users.filter(user=user).exists())):
                return None, 'دسترسی غیرمجاز'
            return chat, None
        except Chat.DoesNotExist:
            return None, 'چت یافت نشد'
        except Exception as e:
            return None, f'خطا در دریافت چت: {str(e)}'

    @extend_schema(summary="دریافت جزئیات چت", responses={200: ChatSerializer})
    def get(self, request, chat_id):
        """دریافت جزئیات یک چت"""
        chat, error = self.get_chat(chat_id, request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if 'دسترسی غیرمجاز' in error else status.HTTP_404_NOT_FOUND
            return Response({'error': error}, status=status_code)
            
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary="به‌روزرسانی چت", request=ChatSerializer, responses={200: ChatSerializer})
    def put(self, request, chat_id):
        """به‌روزرسانی یک چت"""
        chat, error = self.get_chat(chat_id, request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if 'دسترسی غیرمجاز' in error else status.HTTP_404_NOT_FOUND
            return Response({'error': error}, status=status_code)
            
        serializer = ChatSerializer(chat, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            chat = serializer.save()
            return Response(ChatSerializer(chat, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="حذف چت", responses={204: None})
    def delete(self, request, chat_id):
        """حذف یک چت"""
        chat, error = self.get_chat(chat_id, request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if 'دسترسی غیرمجاز' in error else status.HTTP_404_NOT_FOUND
            return Response({'error': error}, status=status_code)
            
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageListCreateView(APIView):
    """API برای دریافت لیست و ایجاد پیام‌ها در یک چت"""
    permission_classes = [IsAuthenticated]

    def get_chat(self, chat_id, user):
        """دریافت چت با بررسی دسترسی"""
        try:
            chat = Chat.objects.get(id=chat_id)
            # بررسی دسترسی: کاربر باید شرکت‌کننده در چت یا عضو کسب‌وکار مرتبط باشد
            if not (chat.participants.filter(id=user.id).exists() or 
                   (chat.business and chat.business.users.filter(user=user).exists())):
                return None, 'دسترسی غیرمجاز'
            return chat, None
        except Chat.DoesNotExist:
            return None, 'چت یافت نشد'
        except Exception as e:
            return None, f'خطا در دریافت چت: {str(e)}'

    @extend_schema(summary="دریافت پیام‌های چت", responses={200: MessageSerializer(many=True)})
    def get(self, request, chat_id):
        """دریافت لیست پیام‌های یک چت"""
        chat, error = self.get_chat(chat_id, request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if 'دسترسی غیرمجاز' in error else status.HTTP_404_NOT_FOUND
            return Response({'error': error}, status=status_code)
            
        messages = Message.objects.filter(chat=chat)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary="ارسال پیام جدید", request=MessageSerializer, responses={201: MessageSerializer})
    def post(self, request, chat_id):
        """ارسال پیام جدید در یک چت"""
        chat, error = self.get_chat(chat_id, request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if 'دسترسی غیرمجاز' in error else status.HTTP_404_NOT_FOUND
            return Response({'error': error}, status=status_code)
            
        data = {**request.data, 'chat': chat_id, 'sender': request.user.id}
        serializer = MessageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                MessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageDetailView(APIView):
    """API برای علامت‌گذاری پیام به‌عنوان خوانده‌شده"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="علامت‌گذاری پیام به‌عنوان خوانده‌شده", responses={200: MessageSerializer})
    def post(self, request, message_id):
        """علامت‌گذاری پیام به‌عنوان خوانده‌شده"""
        try:
            message = Message.objects.get(id=message_id)
            
            # بررسی دسترسی
            chat = message.chat
            if not (chat.participants.filter(id=request.user.id).exists() or 
                   (chat.business and chat.business.users.filter(user=request.user).exists())):
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            # اگر کاربر فرستنده پیام نباشد
            if message.sender != request.user:
                message.is_read = True
                message.save()
                
            serializer = MessageSerializer(message, context={'request': request})
            return Response(serializer.data)
        except Message.DoesNotExist:
            return Response({'error': 'پیام یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': f'خطا در علامت‌گذاری پیام: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationListView(APIView):
    """API برای دریافت لیست اعلانات"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست اعلانات", responses={200: NotificationSerializer(many=True)})
    def get(self, request):
        """دریافت لیست اعلانات کاربر"""
        try:
            # اعلانات مربوط به کاربر یا کسب‌وکارهای او
            notifications = Notification.objects.filter(
                Q(user=request.user) | 
                Q(business__users__user=request.user)
            ).distinct()
            
            # فیلتر بر اساس وضعیت خوانده‌شده
            is_read = request.query_params.get('is_read')
            if is_read is not None:
                notifications = notifications.filter(is_read=is_read.lower() == 'true')
                
            # فیلتر بر اساس نوع اعلان
            notification_type = request.query_params.get('type')
            if notification_type:
                notifications = notifications.filter(type=notification_type)
                
            serializer = NotificationSerializer(notifications, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'خطا در دریافت اعلانات: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationMarkReadView(APIView):
    """API برای علامت‌گذاری اعلان به‌عنوان خوانده‌شده"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="علامت‌گذاری اعلان به‌عنوان خوانده‌شده", responses={200: NotificationSerializer})
    def post(self, request, notification_id):
        """علامت‌گذاری اعلان به‌عنوان خوانده‌شده"""
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # بررسی دسترسی
            if notification.user != request.user and not (
                notification.business and notification.business.users.filter(user=request.user).exists()):
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            notification.is_read = True
            notification.save()
            
            serializer = NotificationSerializer(notification, context={'request': request})
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': 'اعلان یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': f'خطا در علامت‌گذاری اعلان: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
