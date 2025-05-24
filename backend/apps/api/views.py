from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from .models import APIKey, APILog
from .serializers import APIKeySerializer, APILogSerializer
from apps.core.utils import log_error


@api_view(['GET'])
def api_root(request, format=None):
    """
    نقطه شروع API که لینک به تمام ماژول‌های اصلی را ارائه می‌دهد
    """
    return Response({
        'auth': reverse('authentication:root', request=request, format=format),
        'core': reverse('core:root', request=request, format=format),
        'business': reverse('business:root', request=request, format=format),
        'payment': reverse('payment:root', request=request, format=format),
        'designs': reverse('designs:root', request=request, format=format),
        'templates': reverse('templates_app:root', request=request, format=format),
        'orders': reverse('orders:root', request=request, format=format),
        'notification': reverse('notification:root', request=request, format=format),
        'dashboard': reverse('dashboard:root', request=request, format=format),
        'main': reverse('main:root', request=request, format=format),
        'settings': reverse('settings:root', request=request, format=format),
        'reports': reverse('reports:root', request=request, format=format),
        'communication': reverse('communication:root', request=request, format=format),
        'workshop': reverse('workshop:root', request=request, format=format),
        'craft': reverse('craft:root', request=request, format=format),
        'tender': reverse('tender:root', request=request, format=format),
    })

class APIKeyListCreateView(APIView):
    """API برای نمایش لیست و ایجاد کلیدهای API"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست کلیدهای API", responses={200: APIKeySerializer(many=True)})
    def get(self, request):
        try:
            # ادمین همه کلیدها را می‌بیند، کاربر عادی فقط کلیدهای خودش را
            if request.user.is_staff:
                api_keys = APIKey.objects.all()
            else:
                api_keys = APIKey.objects.filter(user=request.user)
            
            # فیلتر بر اساس وضعیت فعال بودن
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                api_keys = api_keys.filter(is_active=is_active.lower() == 'true')
            
            # جستجو
            search = request.query_params.get('search')
            if search:
                api_keys = api_keys.filter(
                    Q(name__icontains=search) | 
                    Q(key__icontains=search)
                )
            
            serializer = APIKeySerializer(api_keys, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving API keys", e)
            return Response(
                {'error': 'خطا در دریافت لیست کلیدهای API'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="ایجاد کلید API جدید", request=APIKeySerializer, responses={201: APIKeySerializer})
    def post(self, request):
        try:
            serializer = APIKeySerializer(data=request.data)
            if serializer.is_valid():
                # تنظیم کاربر برای کلید جدید
                if not request.user.is_staff:
                    serializer.validated_data['user'] = request.user
                
                # تولید کلید تصادفی
                import secrets
                serializer.validated_data['key'] = secrets.token_hex(32)
                
                api_key = serializer.save()
                return Response(
                    APIKeySerializer(api_key).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating API key", e)
            return Response(
                {'error': 'خطا در ایجاد کلید API'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class APIKeyDetailView(APIView):
    """API برای نمایش، ویرایش و حذف کلید API"""
    permission_classes = [IsAuthenticated]

    def get_api_key(self, key_id, user):
        try:
            if user.is_staff:
                return APIKey.objects.get(id=key_id)
            return APIKey.objects.get(id=key_id, user=user)
        except APIKey.DoesNotExist:
            return None

    @extend_schema(summary="دریافت جزئیات کلید API", responses={200: APIKeySerializer})
    def get(self, request, key_id):
        api_key = self.get_api_key(key_id, request.user)
        if not api_key:
            return Response(
                {'error': 'کلید API یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = APIKeySerializer(api_key)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش کلید API", request=APIKeySerializer, responses={200: APIKeySerializer})
    def put(self, request, key_id):
        api_key = self.get_api_key(key_id, request.user)
        if not api_key:
            return Response(
                {'error': 'کلید API یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            serializer = APIKeySerializer(api_key, data=request.data, partial=True)
            if serializer.is_valid():
                # کاربر عادی نمی‌تواند کاربر کلید را تغییر دهد
                if not request.user.is_staff:
                    serializer.validated_data.pop('user', None)
                
                api_key = serializer.save()
                return Response(APIKeySerializer(api_key).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error updating API key", e)
            return Response(
                {'error': 'خطا در به‌روزرسانی کلید API'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="حذف کلید API")
    def delete(self, request, key_id):
        api_key = self.get_api_key(key_id, request.user)
        if not api_key:
            return Response(
                {'error': 'کلید API یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            api_key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("Error deleting API key", e)
            return Response(
                {'error': 'خطا در حذف کلید API'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class APILogListView(APIView):
    """API برای نمایش لیست لاگ‌های API"""
    permission_classes = [IsAdminUser]  # فقط ادمین می‌تواند لاگ‌ها را ببیند

    @extend_schema(summary="دریافت لیست لاگ‌های API", responses={200: APILogSerializer(many=True)})
    def get(self, request):
        try:
            logs = APILog.objects.all()
            
            # فیلتر بر اساس کاربر
            user_id = request.query_params.get('user_id')
            if user_id:
                logs = logs.filter(user_id=user_id)
            
            # فیلتر بر اساس کلید API
            api_key_id = request.query_params.get('api_key_id')
            if api_key_id:
                logs = logs.filter(api_key_id=api_key_id)
            
            # فیلتر بر اساس متد
            method = request.query_params.get('method')
            if method:
                logs = logs.filter(method=method.upper())
            
            # فیلتر بر اساس کد پاسخ
            response_code = request.query_params.get('response_code')
            if response_code:
                logs = logs.filter(response_code=response_code)
            
            # فیلتر بر اساس مسیر
            path = request.query_params.get('path')
            if path:
                logs = logs.filter(path__icontains=path)
            
            # فیلتر بر اساس IP
            ip_address = request.query_params.get('ip_address')
            if ip_address:
                logs = logs.filter(ip_address=ip_address)
            
            # محدود کردن نتایج
            limit = int(request.query_params.get('limit', 100))
            logs = logs[:limit]
            
            serializer = APILogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving API logs", e)
            return Response(
                {'error': 'خطا در دریافت لیست لاگ‌های API'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
