# بهبودهای امنیتی برای پروژه Pardach
# Security Improvements for Pardach Project

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import permission_classes, throttle_classes
import logging
import re

logger = logging.getLogger(__name__)

# 1. Custom Permission Classes
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user

# 2. Input Validation Decorators
def validate_persian_text(value):
    """اعتبار سنجی متن فارسی"""
    if not re.match(r'^[\u0600-\u06FF\s\w]+$', value):
        raise ValidationError('متن باید شامل حروف فارسی معتبر باشد.')

def validate_phone_number(value):
    """اعتبار سنجی شماره تلفن ایرانی"""
    phone_regex = RegexValidator(
        regex=r'^(\+98|0)?9\d{9}$',
        message="شماره تلفن باید با فرمت 09XXXXXXXXX باشد"
    )
    phone_regex(value)

# 3. Rate Limiting
class OrderRateThrottle(UserRateThrottle):
    scope = 'orders'
    rate = '10/min'  # حداکثر 10 سفارش در دقیقه

class APIThrottle(UserRateThrottle):
    scope = 'api'
    rate = '100/hour'  # حداکثر 100 درخواست در ساعت

# 4. Secure API Views
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SecureOrderViewSet(viewsets.ModelViewSet):
    """ViewSet امن برای مدیریت سفارش‌ها"""
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [OrderRateThrottle]
    
    def get_queryset(self):
        # فقط سفارش‌های کاربر جاری را نمایش دهد
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # ثبت log برای سفارش جدید
        logger.info(f"New order created by user: {self.request.user.username}")
        serializer.save(user=self.request.user)

# 5. Data Sanitization
def sanitize_input(data):
    """پاک‌سازی داده‌های ورودی"""
    if isinstance(data, str):
        # حذف کاراکترهای مخرب
        data = re.sub(r'[<>"\']', '', data)
        # حذف فاصله‌های اضافی
        data = data.strip()
    return data

# 6. Secure File Upload
def validate_image_file(file):
    """اعتبار سنجی فایل تصویر"""
    # بررسی اندازه فایل (حداکثر 5MB)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('اندازه فایل نباید از 5 مگابایت بیشتر باشد.')
    
    # بررسی نوع فایل
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise ValidationError('فقط فایل‌های JPEG، PNG و GIF مجاز هستند.')
    
    # بررسی امضای فایل
    file_signatures = {
        b'\xff\xd8\xff': 'jpeg',
        b'\x89\x50\x4e\x47': 'png',
        b'\x47\x49\x46': 'gif'
    }
    
    file.seek(0)
    header = file.read(4)
    file.seek(0)
    
    for signature, file_type in file_signatures.items():
        if header.startswith(signature):
            return True
    
    raise ValidationError('فایل نامعتبر است.')

# 7. Secure Authentication
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class SecureAuthenticationBackend(BaseBackend):
    """سیستم احراز هویت امن"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # محدودیت تعداد تلاش‌های ناموفق
        if self.check_failed_attempts(username):
            logger.warning(f"Too many failed attempts for username: {username}")
            return None
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # ریست کردن تعداد تلاش‌های ناموفق
                self.reset_failed_attempts(username)
                logger.info(f"Successful login for user: {username}")
                return user
            else:
                self.increment_failed_attempts(username)
                logger.warning(f"Failed login attempt for user: {username}")
        except User.DoesNotExist:
            logger.warning(f"Login attempt for non-existent user: {username}")
        
        return None
    
    def check_failed_attempts(self, username):
        # بررسی تعداد تلاش‌های ناموفق (پیاده‌سازی با Redis یا Database)
        # Implementation would depend on your caching solution
        return False
    
    def increment_failed_attempts(self, username):
        # افزایش تعداد تلاش‌های ناموفق
        pass
    
    def reset_failed_attempts(self, username):
        # ریست کردن تعداد تلاش‌های ناموفق
        pass

# 8. Secure Settings Middleware
class SecurityHeadersMiddleware:
    """Middleware برای اضافه کردن هدرهای امنیتی"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # اضافه کردن هدرهای امنیتی
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response 