from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.orders.models import Order
from apps.payment.models import Payment
from apps.notification.models import Notification
from apps.designs.models import Design
from apps.business.models import Business, BusinessActivity
from apps.communication.models import Chat, Message
from apps.reports.models import Report
from apps.core.utils import log_error, to_jalali
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .serializers import MainPageResponseSerializer, PromotionSerializer, MainPageSettingSerializer, WelcomeDataSerializer
from django.utils import timezone
from django.db import models
from apps.core.models import SystemSetting
from .models import Promotion, MainPageSetting
import jdatetime
from django.http import JsonResponse

class MainPageSummaryView(APIView):
    """API برای دریافت داده‌های خلاصه صفحه اصلی"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="دریافت داده‌های صفحه اصلی",
        description="دریافت خلاصه داده‌های سفارش‌ها، پرداخت‌ها، اعلانات، چت‌ها و منوی ناوبری",
        responses={200: MainPageResponseSerializer}
    )
    def get(self, request):
        try:
            # محدوده زمانی برای داده‌های اخیر
            days = int(request.query_params.get('days', 7))
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # فیلتر براساس نقش کاربر
            is_admin = request.user.is_staff

            # خلاصه سفارش‌ها
            orders_query = Order.objects.filter(created_at__range=[start_date, end_date])
            if not is_admin:
                orders_query = orders_query.filter(user=request.user)
            recent_orders = list(orders_query[:5].values('id', 'total_price', 'status', 'created_at'))
            order_count = orders_query.count()

            # خلاصه پرداخت‌ها
            payments_query = Payment.objects.filter(created_at__range=[start_date, end_date], status='successful')
            if not is_admin:
                payments_query = payments_query.filter(user=request.user)
            recent_payments = list(payments_query[:5].values('id', 'amount', 'status', 'created_at'))
            payment_count = payments_query.count()

            # خلاصه اعلانات
            notifications_query = Notification.objects.filter(
                Q(user=request.user) | Q(all_users=True),
                created_at__range=[start_date, end_date]
            )
            recent_notifications = list(notifications_query[:5].values('id', 'title', 'message', 'read', 'link', 'created_at'))
            unread_notifications = notifications_query.filter(read=False).count()

            # خلاصه چت‌ها
            chats_query = Chat.objects.filter(participants=request.user, created_at__range=[start_date, end_date])
            recent_chats = list(chats_query[:5].values('id', 'title', 'created_at'))

            # خلاصه طرح‌ها (برای طراحان یا ادمین‌ها)
            designs_query = Design.objects.filter(created_at__range=[start_date, end_date])
            if not is_admin:
                designs_query = designs_query.filter(created_by=request.user)
            recent_designs = list(designs_query[:5].values('id', 'title', 'image', 'created_at'))

            # تبلیغات (از دیتابیس)
            promotions = Promotion.objects.filter(is_active=True).order_by('order', '-created_at')
            promotions_data = PromotionSerializer(promotions, many=True).data

            # اگر تبلیغاتی در دیتابیس نبود، از مقادیر پیش‌فرض استفاده کنیم
            if not promotions.exists():
                promotions_data = [
                    {'title': 'طرح‌های جدید', 'image': '/static/images/promo1.jpg', 'link': '/designs', 'description': 'مشاهده جدیدترین طرح‌های ما'},
                    {'title': 'تخفیف سفارشات', 'image': '/static/images/promo2.jpg', 'link': '/orders', 'description': 'تخفیف ویژه برای سفارشات بیش از ۵۰۰ هزار تومان'},
                    {'title': 'گزارش‌های تحلیلی', 'image': '/static/images/promo3.jpg', 'link': '/reports', 'description': 'دسترسی به گزارش‌های تحلیلی کسب و کار'},
                ]

            # منوی ناوبری با نمایش مختلف برای کاربران عادی و ادمین
            navigation = [
                {'title': 'طرح‌ها', 'icon': 'fa-paint-brush', 'link': '/designs', 'visible': True},
                {'title': 'قالب‌ها', 'icon': 'fa-layer-group', 'link': '/templates', 'visible': True},
                {'title': 'سفارش‌ها', 'icon': 'fa-shopping-cart', 'link': '/orders', 'visible': True},
                {'title': 'پرداخت‌ها', 'icon': 'fa-credit-card', 'link': '/payments', 'visible': True},
                {'title': 'چت‌ها', 'icon': 'fa-comments', 'link': '/chats', 'visible': True},
                {'title': 'اعلانات', 'icon': 'fa-bell', 'link': '/notifications', 'visible': True},
                {'title': 'گزارش‌ها', 'icon': 'fa-chart-bar', 'link': '/reports', 'visible': is_admin},
                {'title': 'کسب‌وکارها', 'icon': 'fa-briefcase', 'link': '/businesses', 'visible': is_admin},
                {'title': 'داشبورد', 'icon': 'fa-tachometer-alt', 'link': '/dashboard', 'visible': is_admin},
            ]

            # بخش خوش‌آمدگویی
            jalali_now = jdatetime.datetime.now()
            welcome_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'today_date_jalali': f"{jalali_now.year}/{jalali_now.month}/{jalali_now.day}",
                'last_login_jalali': to_jalali(request.user.last_login) if request.user.last_login else None,
                'unread_count': unread_notifications,
                'order_in_progress': orders_query.filter(status__in=['pending', 'processing']).count()
            }

            # تبدیل تاریخ‌ها به شمسی
            for item in recent_orders:
                item['created_at'] = to_jalali(item['created_at'])
            
            for item in recent_payments:
                item['created_at'] = to_jalali(item['created_at'])
            
            for item in recent_notifications:
                item['created_at'] = to_jalali(item['created_at'])
            
            for item in recent_chats:
                item['created_at'] = to_jalali(item['created_at'])
            
            for item in recent_designs:
                item['created_at'] = to_jalali(item['created_at'])

            return Response({
                'summary': {
                    'order_count': order_count,
                    'payment_count': payment_count,
                    'unread_notifications': unread_notifications,
                    'recent_orders': recent_orders,
                    'recent_payments': recent_payments,
                    'recent_notifications': recent_notifications,
                    'recent_chats': recent_chats,
                    'recent_designs': recent_designs,
                },
                'promotions': promotions_data,
                'navigation': navigation,
                'welcome_data': welcome_data
            })
        except Exception as e:
            log_error("خطا در دریافت داده‌های صفحه اصلی", e)
            return Response({'error': 'خطا در دریافت داده‌های صفحه اصلی'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MainSummaryView(APIView):
    """API برای دریافت داده‌های خلاصه سیستم"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="دریافت داده‌های خلاصه",
        description="دریافت خلاصه داده‌های کلی سیستم برای داشبورد اصلی",
        responses={200: MainPageResponseSerializer}
    )
    def get(self, request):
        try:
            # محدوده زمانی برای داده‌های اخیر
            days = int(request.query_params.get('days', 30))
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # فیلتر براساس نقش کاربر
            is_admin = request.user.is_staff

            # کاربر عادی فقط آمار خودش را می‌بیند
            if not is_admin:
                user_filter = Q(user=request.user)
            else:
                user_filter = Q()

            # آمار کلی سیستم
            order_count = Order.objects.filter(user_filter, created_at__range=[start_date, end_date]).count()
            payment_sum = Payment.objects.filter(user_filter, status='successful', created_at__range=[start_date, end_date]).aggregate(
                total=Sum('amount'))['total'] or 0
            designs_count = Design.objects.filter(created_at__range=[start_date, end_date]).count()
            businesses_count = Business.objects.filter(created_at__range=[start_date, end_date]).count()
            
            # آمار فعالیت‌ها
            activities = []
            if is_admin:
                recent_activities = BusinessActivity.objects.all().order_by('-created_at')[:10]
                for activity in recent_activities:
                    activities.append({
                        'id': activity.id,
                        'business_name': activity.business.name if activity.business else '',
                        'action': activity.action,
                        'created_at': to_jalali(activity.created_at)
                    })

            # تبدیل تاریخ به شمسی
            jalali_now = jdatetime.datetime.now()
            
            return Response({
                'summary': {
                    'order_count': order_count,
                    'payment_sum': payment_sum,
                    'designs_count': designs_count,
                    'businesses_count': businesses_count,
                    'today_date_jalali': f"{jalali_now.year}/{jalali_now.month}/{jalali_now.day}",
                },
                'activities': activities,
                'user_is_admin': is_admin
            })
        except Exception as e:
            log_error("خطا در دریافت داده‌های خلاصه", e)
            return Response({'error': 'خطا در دریافت داده‌های خلاصه'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PromotionListView(APIView):
    """API برای مدیریت تبلیغات صفحه اصلی"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="دریافت لیست تبلیغات",
        description="دریافت لیست تمامی تبلیغات فعال",
        responses={200: PromotionSerializer(many=True)}
    )
    def get(self, request):
        try:
            # فقط ادمین می‌تواند همه تبلیغات را ببیند
            if request.user.is_staff:
                promotions = Promotion.objects.all().order_by('order')
            else:
                promotions = Promotion.objects.filter(is_active=True).order_by('order')
                
            serializer = PromotionSerializer(promotions, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت تبلیغات", e)
            return Response({'error': 'خطا در دریافت تبلیغات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="ایجاد تبلیغ جدید",
        description="ایجاد یک تبلیغ جدید (فقط برای ادمین)",
        request=PromotionSerializer,
        responses={201: PromotionSerializer}
    )
    def post(self, request):
        # فقط ادمین می‌تواند تبلیغ جدید ایجاد کند
        if not request.user.is_staff:
            return Response({'error': 'شما اجازه دسترسی به این بخش را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromotionDetailView(APIView):
    """API برای مدیریت یک تبلیغ خاص"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Promotion.objects.get(pk=pk)
        except Promotion.DoesNotExist:
            return None
    
    @extend_schema(
        summary="دریافت جزئیات تبلیغ",
        description="دریافت جزئیات یک تبلیغ خاص",
        responses={200: PromotionSerializer}
    )
    def get(self, request, pk):
        promotion = self.get_object(pk)
        if not promotion:
            return Response({'error': 'تبلیغ مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        # اگر کاربر ادمین نیست و تبلیغ غیرفعال است، دسترسی ندارد
        if not request.user.is_staff and not promotion.is_active:
            return Response({'error': 'شما اجازه دسترسی به این تبلیغ را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = PromotionSerializer(promotion)
        return Response(serializer.data)
    
    @extend_schema(
        summary="بروزرسانی تبلیغ",
        description="بروزرسانی یک تبلیغ خاص (فقط برای ادمین)",
        request=PromotionSerializer,
        responses={200: PromotionSerializer}
    )
    def put(self, request, pk):
        # فقط ادمین می‌تواند تبلیغ را بروزرسانی کند
        if not request.user.is_staff:
            return Response({'error': 'شما اجازه دسترسی به این بخش را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        promotion = self.get_object(pk)
        if not promotion:
            return Response({'error': 'تبلیغ مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = PromotionSerializer(promotion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="حذف تبلیغ",
        description="حذف یک تبلیغ خاص (فقط برای ادمین)",
        responses={204: None}
    )
    def delete(self, request, pk):
        # فقط ادمین می‌تواند تبلیغ را حذف کند
        if not request.user.is_staff:
            return Response({'error': 'شما اجازه دسترسی به این بخش را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        promotion = self.get_object(pk)
        if not promotion:
            return Response({'error': 'تبلیغ مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        promotion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MainSettingView(APIView):
    """API برای مدیریت تنظیمات صفحه اصلی"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="دریافت تنظیمات صفحه اصلی",
        description="دریافت تمامی تنظیمات فعال صفحه اصلی",
        responses={200: MainPageSettingSerializer(many=True)}
    )
    def get(self, request):
        # فقط ادمین می‌تواند تنظیمات را ببیند
        if not request.user.is_staff:
            return Response({'error': 'شما اجازه دسترسی به این بخش را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        settings = MainPageSetting.objects.filter(is_active=True)
        serializer = MainPageSettingSerializer(settings, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="ایجاد یا بروزرسانی تنظیم",
        description="ایجاد یا بروزرسانی یک تنظیم صفحه اصلی (فقط برای ادمین)",
        request=MainPageSettingSerializer,
        responses={200: MainPageSettingSerializer}
    )
    def post(self, request):
        # فقط ادمین می‌تواند تنظیمات را ایجاد یا بروزرسانی کند
        if not request.user.is_staff:
            return Response({'error': 'شما اجازه دسترسی به این بخش را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        # بررسی وجود تنظیم با کلید مشابه
        key = request.data.get('key')
        setting, created = MainPageSetting.objects.get_or_create(key=key)
        
        serializer = MainPageSettingSerializer(setting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return JsonResponse({
        'status': 'success',
        'message': 'به API سرور خوش آمدید',
        'version': '1.0.0'
    })
