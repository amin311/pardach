from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Sum
from django.utils import timezone

from .models import Order, OrderItem, OrderSection, OrderStage, GarmentDetails
from .serializers import (
    OrderSerializer, OrderItemSerializer, OrderSectionSerializer,
    OrderStageSerializer, GarmentDetailsSerializer
)
from apps.core.permissions import IsOwnerOrAdmin

class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت سفارش‌ها"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'print_type', 'fabric_type', 'business']
    search_fields = ['customer__username', 'customer__first_name', 'customer__last_name', 'notes']
    ordering_fields = ['created_at', 'total_price', 'delivery_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """فیلتر سفارش‌ها بر اساس نقش کاربر"""
        user = self.request.user
        
        if user.is_staff:
            # مدیران سیستم دسترسی به همه سفارش‌ها
            return Order.objects.all().select_related(
                'customer', 'business'
            ).prefetch_related(
                'items', 'sections', 'stages'
            )
        
        # فیلتر بر اساس نقش
        queryset = Order.objects.none()
        
        # مشتریان فقط سفارش‌های خودشان
        queryset |= Order.objects.filter(customer=user)
        
        # صاحبان کسب‌وکار سفارش‌های تخصیص یافته
        if hasattr(user, 'business_users'):
            business_ids = user.business_users.values_list('business_id', flat=True)
            queryset |= Order.objects.filter(business_id__in=business_ids)
        
        return queryset.distinct().select_related(
            'customer', 'business'
        ).prefetch_related(
            'items', 'sections', 'stages'
        )

    def perform_create(self, serializer):
        """تنظیم مشتری هنگام ایجاد سفارش"""
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """تأیید سفارش"""
        order = self.get_object()
        
        if order.status != 'draft':
            return Response(
                {'error': 'فقط سفارش‌های پیش‌نویس قابل تأیید هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'confirmed'
        order.save(update_fields=['status'])
        
        return Response({'message': 'سفارش تأیید شد'})

    @action(detail=True, methods=['post'])
    def start_set_design(self, request, pk=None):
        """شروع فرآیند ست‌بندی"""
        order = self.get_object()
        
        if order.status != 'confirmed':
            return Response(
                {'error': 'فقط سفارش‌های تأیید شده قابل ست‌بندی هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'set_design'
        order.save(update_fields=['status'])
        
        return Response({'message': 'فرآیند ست‌بندی آغاز شد'})

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """آمار سفارش‌ها برای داشبورد"""
        queryset = self.get_queryset()
        
        stats = {
            'total_orders': queryset.count(),
            'pending_orders': queryset.filter(status='pending').count(),
            'in_progress_orders': queryset.filter(status__in=['confirmed', 'set_design', 'printing']).count(),
            'completed_orders': queryset.filter(status='completed').count(),
            'total_revenue': queryset.filter(is_paid=True).aggregate(
                total=Sum('total_price')
            )['total'] or 0,
            'orders_by_status': dict(
                queryset.values_list('status').annotate(count=Count('id'))
            )
        }
        
        return Response(stats)

class OrderSectionViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت بخش‌های سفارش"""
    serializer_class = OrderSectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'location', 'design', 'is_inner_print']

    def get_queryset(self):
        """فیلتر بخش‌ها بر اساس دسترسی به سفارش"""
        user = self.request.user
        
        if user.is_staff:
            return OrderSection.objects.all()
        
        # دسترسی بر اساس مالکیت سفارش
        accessible_orders = Order.objects.filter(
            Q(customer=user) |
            Q(business__users__user=user)
        ).values_list('id', flat=True)
        
        return OrderSection.objects.filter(order_id__in=accessible_orders)

class OrderStageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده مراحل سفارش (فقط خواندنی)"""
    serializer_class = OrderStageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'stage_type', 'status', 'assigned_to']
    ordering = ['order', 'stage_type']

    def get_queryset(self):
        """فیلتر مراحل بر اساس دسترسی به سفارش"""
        user = self.request.user
        
        if user.is_staff:
            return OrderStage.objects.all()
        
        # دسترسی بر اساس مالکیت سفارش
        accessible_orders = Order.objects.filter(
            Q(customer=user) |
            Q(business__users__user=user)
        ).values_list('id', flat=True)
        
        return OrderStage.objects.filter(order_id__in=accessible_orders)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """علامت‌گذاری مرحله به عنوان تکمیل شده"""
        stage = self.get_object()
        
        if stage.status == 'completed':
            return Response(
                {'error': 'این مرحله قبلاً تکمیل شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # بررسی مجوز تکمیل
        if stage.assigned_to and stage.assigned_to != request.user and not request.user.is_staff:
            return Response(
                {'error': 'فقط فرد مسئول یا مدیر می‌تواند مرحله را تکمیل کند'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stage.status = 'completed'
        stage.finished_at = timezone.now()
        stage.save(update_fields=['status', 'finished_at'])
        
        return Response({'message': 'مرحله با موفقیت تکمیل شد'})

class OrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت آیتم‌های سفارش"""
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'design']

    def get_queryset(self):
        """فیلتر آیتم‌ها بر اساس دسترسی به سفارش"""
        user = self.request.user
        
        if user.is_staff:
            return OrderItem.objects.all()
        
        # فقط آیتم‌های سفارش‌هایی که کاربر به آنها دسترسی دارد
        accessible_orders = Order.objects.filter(
            Q(customer=user) |
            Q(business__users__user=user)
        ).values_list('id', flat=True)
        
        return OrderItem.objects.filter(order_id__in=accessible_orders) 