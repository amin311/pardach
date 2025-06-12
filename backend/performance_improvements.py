# بهبودهای کارایی برای پروژه Pardach
# Performance Improvements for Pardach Project

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db import connection
from django.db.models import Prefetch, Q, Count, Sum
from django.conf import settings
import redis
import json
import time
from functools import wraps

# 1. Redis Cache Configuration
redis_client = redis.Redis(
    host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
    port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
    db=0,
    decode_responses=True
)

# 2. Custom Caching Decorators
def cache_result(timeout=300, key_prefix=''):
    """کش کردن نتایج توابع"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # ساخت کلید کش
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # بررسی وجود در کش
            result = cache.get(cache_key)
            if result is not None:
                return json.loads(result)
            
            # اجرای تابع و ذخیره در کش
            result = func(*args, **kwargs)
            cache.set(cache_key, json.dumps(result, default=str), timeout)
            return result
        return wrapper
    return decorator

# 3. Database Query Optimization
class OptimizedQueryMixin:
    """Mixin برای بهینه‌سازی کوئری‌های دیتابیس"""
    
    def get_optimized_queryset(self):
        """دریافت QuerySet بهینه‌شده"""
        return self.get_queryset().select_related().prefetch_related()
    
    def get_with_relations(self, pk):
        """دریافت آبجکت همراه با روابط"""
        return self.get_queryset().select_related(
            'user', 'category'
        ).prefetch_related(
            'items', 'notifications'
        ).get(pk=pk)

# 4. Efficient Pagination
from rest_framework.pagination import PageNumberPagination

class OptimizedPagination(PageNumberPagination):
    """صفحه‌بندی بهینه‌شده"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        # اضافه کردن اطلاعات کش
        response = super().get_paginated_response(data)
        response.data['cache_info'] = {
            'cached_at': time.time(),
            'ttl': 300
        }
        return response

# 5. Bulk Operations
class BulkOperationsMixin:
    """عملیات انبوه برای بهبود کارایی"""
    
    def bulk_create_orders(self, orders_data):
        """ایجاد انبوه سفارش‌ها"""
        orders = []
        for order_data in orders_data:
            orders.append(Order(**order_data))
        
        return Order.objects.bulk_create(orders, batch_size=100)
    
    def bulk_update_status(self, order_ids, new_status):
        """به‌روزرسانی انبوه وضعیت سفارش‌ها"""
        return Order.objects.filter(
            id__in=order_ids
        ).update(status=new_status)

# 6. Database Connection Pooling
class DatabaseOptimizations:
    """بهینه‌سازی‌های دیتابیس"""
    
    @staticmethod
    def get_db_stats():
        """آمار کوئری‌های دیتابیس"""
        return {
            'total_queries': len(connection.queries),
            'queries': connection.queries[-10:]  # آخرین 10 کوئری
        }
    
    @staticmethod
    def reset_queries():
        """ریست کردن آمار کوئری‌ها"""
        connection.queries_log.clear()

# 7. Async Views for Heavy Operations
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import asyncio

@require_http_methods(["POST"])
async def async_process_orders(request):
    """پردازش ناهمزمان سفارش‌ها"""
    try:
        # پردازش سنگین در background
        await asyncio.sleep(0.1)  # شبیه‌سازی پردازش
        
        # به‌روزرسانی وضعیت در کش
        cache.set('processing_status', 'completed', 300)
        
        return JsonResponse({
            'status': 'success',
            'message': 'پردازش با موفقیت انجام شد'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# 8. Memory Usage Optimization
import gc
from django.core.management.base import BaseCommand

class MemoryOptimization:
    """بهینه‌سازی استفاده از حافظه"""
    
    @staticmethod
    def cleanup_memory():
        """پاک‌سازی حافظه"""
        gc.collect()
        return gc.get_stats()
    
    @staticmethod
    def get_memory_usage():
        """دریافت میزان استفاده از حافظه"""
        import psutil
        process = psutil.Process()
        return {
            'memory_percent': process.memory_percent(),
            'memory_info': process.memory_info()._asdict()
        }

# 9. API Response Compression
from django.middleware.gzip import GZipMiddleware

class APICompressionMiddleware(GZipMiddleware):
    """فشرده‌سازی پاسخ‌های API"""
    
    def process_response(self, request, response):
        # فشرده‌سازی فقط برای API responses
        if request.path.startswith('/api/'):
            response = super().process_response(request, response)
            response['Content-Encoding'] = 'gzip'
        return response

# 10. Cached ViewSets
@method_decorator(cache_page(60 * 5), name='list')  # کش 5 دقیقه‌ای
@method_decorator(cache_page(60 * 15), name='retrieve')  # کش 15 دقیقه‌ای
class CachedOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet کش‌شده برای سفارش‌ها"""
    
    def get_queryset(self):
        # بهینه‌سازی کوئری
        return Order.objects.select_related(
            'user', 'workshop'
        ).prefetch_related(
            'items', 'notifications'
        ).order_by('-created_at')
    
    @cache_result(timeout=600, key_prefix='order_stats')
    def get_order_statistics(self):
        """آمار سفارش‌ها با کش"""
        return {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
            'total_revenue': Order.objects.aggregate(
                total=Sum('total_price')
            )['total'] or 0
        }

# 11. Search Optimization
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchOptimization:
    """بهینه‌سازی جستجو"""
    
    @staticmethod
    def search_orders(query, user=None):
        """جستجوی بهینه در سفارش‌ها"""
        # استفاده از PostgreSQL Full Text Search
        search_vector = SearchVector('title', 'description')
        search_query = SearchQuery(query)
        
        queryset = Order.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query)
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.order_by('-rank')

# 12. Background Tasks
import celery
from celery import shared_task

@shared_task
def process_order_background(order_id):
    """پردازش سفارش در background"""
    try:
        order = Order.objects.get(id=order_id)
        # پردازش سفارش
        order.status = 'processing'
        order.save()
        
        # ارسال نوتیفیکیشن
        send_notification.delay(order.user.id, f'سفارش {order.id} در حال پردازش است')
        
        return f'Order {order_id} processed successfully'
    except Order.DoesNotExist:
        return f'Order {order_id} not found'

@shared_task
def send_notification(user_id, message):
    """ارسال نوتیفیکیشن در background"""
    # پیاده‌سازی ارسال نوتیفیکیشن
    pass 