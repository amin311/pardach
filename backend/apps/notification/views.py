from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from .models import Notification, NotificationCategory
from .serializers import NotificationSerializer, NotificationCategorySerializer
from apps.core.utils import log_error
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationCategoryListCreateView(APIView):
    """API برای دریافت لیست و ایجاد دسته‌بندی اعلانات"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست دسته‌بندی‌های اعلان", responses={200: NotificationCategorySerializer(many=True)})
    def get(self, request):
        try:
            categories = NotificationCategory.objects.all()
            serializer = NotificationCategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت دسته‌بندی‌های اعلان", e)
            return Response({'error': 'خطا در دریافت اطلاعات دسته‌بندی‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد دسته‌بندی اعلان جدید", request=NotificationCategorySerializer, responses={201: NotificationCategorySerializer})
    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = NotificationCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد دسته‌بندی اعلان", e)
            return Response({'error': 'خطا در ایجاد دسته‌بندی'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationListCreateView(APIView):
    """API برای دریافت لیست و ایجاد اعلانات"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست اعلانات", responses={200: NotificationSerializer(many=True)})
    def get(self, request):
        try:
            # کاربر فقط اعلانات مرتبط با خودش را می‌بیند
            notifications = Notification.objects.filter(
                Q(user=request.user) | 
                Q(business__users__user=request.user)
            ).distinct()
            
            # فیلتر بر اساس پارامترهای درخواست
            is_read = request.query_params.get('is_read')
            is_archived = request.query_params.get('is_archived')
            category_id = request.query_params.get('category_id')
            type_filter = request.query_params.get('type')
            
            if is_read is not None:
                notifications = notifications.filter(is_read=is_read.lower() == 'true')
            if is_archived is not None:
                notifications = notifications.filter(is_archived=is_archived.lower() == 'true')
            if category_id:
                notifications = notifications.filter(category_id=category_id)
            if type_filter:
                notifications = notifications.filter(type=type_filter)
                
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت اعلانات", e)
            return Response({'error': 'خطا در دریافت اطلاعات اعلانات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد اعلان جدید", request=NotificationSerializer, responses={201: NotificationSerializer})
    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = NotificationSerializer(data=request.data)
            if serializer.is_valid():
                notification = serializer.save()
                
                # ارسال اعلان بلادرنگ از طریق WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{notification.user.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': str(notification.id),
                            'title': notification.title,
                            'content': notification.content,
                            'type': notification.type,
                            'is_read': notification.is_read,
                            'link': notification.link,
                            'created_at_jalali': serializer.data['created_at_jalali']
                        }
                    }
                )
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد اعلان", e)
            return Response({'error': 'خطا در ایجاد اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationDetailView(APIView):
    """API برای دریافت، به‌روزرسانی و حذف یک اعلان خاص"""
    permission_classes = [IsAuthenticated]
    
    def get_notification(self, notification_id, user):
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # بررسی دسترسی کاربر
            if notification.user != user and not (notification.business and notification.business.users.filter(user=user).exists()):
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            return notification, None
        except Notification.DoesNotExist:
            return None, Response({'error': 'اعلان یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در دریافت اعلان", e)
            return None, Response({'error': 'خطا در دریافت اطلاعات اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="دریافت جزئیات اعلان", responses={200: NotificationSerializer})
    def get(self, request, notification_id):
        notification, error_response = self.get_notification(notification_id, request.user)
        if error_response:
            return error_response
            
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @extend_schema(summary="به‌روزرسانی اعلان", request=NotificationSerializer, responses={200: NotificationSerializer})
    def put(self, request, notification_id):
        notification, error_response = self.get_notification(notification_id, request.user)
        if error_response:
            return error_response
            
        # فقط مالک اعلان یا مدیر سیستم می‌توانند آن را به‌روزرسانی کنند
        if notification.user != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجوز به‌روزرسانی این اعلان را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            serializer = NotificationSerializer(notification, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در به‌روزرسانی اعلان", e)
            return Response({'error': 'خطا در به‌روزرسانی اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف اعلان", responses={204: None})
    def delete(self, request, notification_id):
        notification, error_response = self.get_notification(notification_id, request.user)
        if error_response:
            return error_response
            
        # فقط مالک اعلان یا مدیر سیستم می‌توانند آن را حذف کنند
        if notification.user != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجوز حذف این اعلان را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("خطا در حذف اعلان", e)
            return Response({'error': 'خطا در حذف اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationMarkReadView(APIView):
    """API برای علامت‌گذاری اعلان به عنوان خوانده‌شده"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="علامت‌گذاری اعلان به عنوان خوانده‌شده", responses={200: NotificationSerializer})
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # بررسی دسترسی کاربر
            if notification.user != request.user and not (notification.business and notification.business.users.filter(user=request.user).exists()):
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            notification.is_read = True
            notification.save()
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': 'اعلان یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در علامت‌گذاری اعلان", e)
            return Response({'error': 'خطا در علامت‌گذاری اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationArchiveView(APIView):
    """API برای آرشیو کردن اعلان"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="آرشیو کردن اعلان", responses={200: NotificationSerializer})
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # بررسی دسترسی کاربر
            if notification.user != request.user and not (notification.business and notification.business.users.filter(user=request.user).exists()):
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            notification.is_archived = True
            notification.save()
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': 'اعلان یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در آرشیو کردن اعلان", e)
            return Response({'error': 'خطا در آرشیو کردن اعلان'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationMarkAllReadView(APIView):
    """API برای علامت‌گذاری همه اعلانات کاربر به عنوان خوانده‌شده"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="علامت‌گذاری همه اعلانات به عنوان خوانده‌شده", responses={200: dict})
    def post(self, request):
        try:
            # فیلتر اعلاناتی که برای کاربر جاری هستند و خوانده نشده‌اند
            updated_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).update(is_read=True)
            
            return Response({
                'status': 'success',
                'message': f'{updated_count} اعلان علامت‌گذاری شد',
                'updated_count': updated_count
            })
        except Exception as e:
            log_error("خطا در علامت‌گذاری همه اعلانات", e)
            return Response({'error': 'خطا در علامت‌گذاری اعلانات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
