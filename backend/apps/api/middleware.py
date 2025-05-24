import time
from django.utils import timezone
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from .models import APIKey, APILog
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class APIKeyMiddleware:
    """میان‌افزار برای احراز هویت و لاگینگ درخواست‌های API"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # اگر مسیر API نیست، رد کردن درخواست
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        start_time = time.time()
        api_key = None
        request_body = None
        
        # ذخیره request.body قبل از هر پردازشی
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = request.body.decode('utf-8')
            except Exception:
                request_body = str(request.body)
        
        try:
            # بررسی کلید API در هدر
            api_key_header = request.headers.get('X-API-Key')
            if api_key_header:
                api_key = APIKey.objects.select_related('user').get(
                    key=api_key_header,
                    is_active=True
                )
                
                # بررسی انقضای کلید
                if api_key.is_expired:
                    return Response(
                        {'error': 'کلید API منقضی شده است'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                # بررسی محدودیت IP
                if api_key.allowed_ips:
                    allowed_ips = [ip.strip() for ip in api_key.allowed_ips.split('\n')]
                    if request.META.get('REMOTE_ADDR') not in allowed_ips:
                        return Response(
                            {'error': 'دسترسی از این IP مجاز نیست'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                
                # بررسی محدودیت تعداد درخواست
                cache_key = f'api_rate_limit_{api_key.id}'
                request_count = cache.get(cache_key, 0)
                if request_count >= api_key.rate_limit:
                    return Response(
                        {'error': 'محدودیت تعداد درخواست روزانه'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                
                # افزایش شمارنده درخواست
                cache.set(cache_key, request_count + 1, timeout=86400)  # 24 ساعت
                
                # به‌روزرسانی زمان آخرین استفاده
                api_key.update_last_used()
                
                # تنظیم کاربر برای درخواست
                request.user = api_key.user
        
        except APIKey.DoesNotExist:
            if not request.path.startswith('/api/auth/'):  # اگر مسیر احراز هویت نیست
                return Response(
                    {'error': 'کلید API نامعتبر است'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # اجرای درخواست
        response = self.get_response(request)
        
        # ثبت لاگ
        execution_time = time.time() - start_time
        
        # تبدیل SimpleLazyObject به نمونه User
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                user = User.objects.get(pk=request.user.pk)
            except User.DoesNotExist:
                user = None
        
        APILog.objects.create(
            api_key=api_key,
            user=user,
            method=request.method,
            path=request.path,
            query_params=str(request.GET),
            request_body=request_body or '',
            response_code=response.status_code,
            response_body=str(getattr(response, 'content', '')),
            ip_address=request.META.get('REMOTE_ADDR'),
            execution_time=execution_time
        )
        
        return response 