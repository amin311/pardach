from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import logging
import uuid

from .models import Payment, Transaction
from apps.orders.models import Order
from .serializers import (
    PaymentSerializer, 
    TransactionSerializer,
    PaymentRequestSerializer,
    PaymentVerifySerializer
)
from .services import get_payment_service
from apps.core.permissions import IsAdminUserOrReadOnly, IsOwnerOrAdmin

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    """مدیریت پرداخت‌ها"""
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        """تعیین مجوزهای دسترسی بر اساس عملیات"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUserOrReadOnly]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """فیلتر پرداخت‌ها بر اساس کاربر"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # اگر کاربر ادمین نیست، فقط پرداخت‌های خودش را نشان می‌دهیم
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(user=user)
        
        # فیلتر بر اساس وضعیت
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, id=None):
        """نمایش تراکنش‌های یک پرداخت خاص"""
        payment = self.get_object()
        transactions = payment.transactions.all().order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """مدیریت تراکنش‌ها (فقط خواندنی)"""
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        """فیلتر تراکنش‌ها بر اساس کاربر"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # اگر کاربر ادمین نیست، فقط تراکنش‌های خودش را نشان می‌دهیم
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(payment__user=user)
        
        return queryset


class PaymentRequestAPIView(APIView):
    """API درخواست پرداخت جدید"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            order_id = data['order_id']
            gateway = data['gateway']
            callback_url = data['callback_url']
            description = data.get('description', '')
            
            try:
                # دریافت سفارش
                order = Order.objects.get(id=order_id)
                
                # بررسی مجوز دسترسی به سفارش
                if order.user != request.user and not request.user.is_staff:
                    return Response(
                        {"error": "شما دسترسی به این سفارش را ندارید"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # ایجاد پرداخت جدید
                payment = Payment.objects.create(
                    user=request.user,
                    order=order,
                    amount=order.total_price,
                    status='pending',
                    transaction_id=str(uuid.uuid4()),
                    gateway=gateway,
                    callback_url=callback_url,
                    description=description
                )
                
                # درخواست پرداخت به درگاه
                payment_service = get_payment_service(payment)
                result = payment_service.request_payment()
                
                if result.get('success'):
                    payment_url = result.get('payment_url')
                    return Response({
                        "success": True,
                        "message": "درخواست پرداخت با موفقیت ایجاد شد",
                        "payment_id": payment.id,
                        "payment_url": payment_url,
                        "transaction_id": payment.transaction_id
                    })
                else:
                    # در صورت شکست، وضعیت پرداخت را آپدیت می‌کنیم
                    payment.status = 'failed'
                    payment.save()
                    
                    return Response({
                        "success": False,
                        "message": result.get('message', 'خطا در ایجاد درخواست پرداخت'),
                        "payment_id": payment.id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Order.DoesNotExist:
                return Response(
                    {"error": "سفارش مورد نظر یافت نشد"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"خطا در ایجاد درخواست پرداخت: {str(e)}")
                return Response(
                    {"error": "خطای سیستمی در پردازش درخواست"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerifyAPIView(APIView):
    """API تایید پرداخت"""
    permission_classes = [permissions.AllowAny]  # دسترسی عمومی برای کال‌بک
    
    def post(self, request):
        """تایید پرداخت - برای فراخوانی از درگاه پرداخت"""
        serializer = PaymentVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            authority = serializer.validated_data['authority']
            status_param = serializer.validated_data['status']
            
            try:
                # پیدا کردن آخرین تراکنش با این شناسه
                transaction = Transaction.objects.filter(
                    authority=authority
                ).order_by('-created_at').first()
                
                if not transaction:
                    return Response(
                        {"error": "تراکنش مورد نظر یافت نشد"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                payment = transaction.payment
                
                # تایید پرداخت در درگاه
                payment_service = get_payment_service(payment)
                result = payment_service.verify_payment(authority, status_param)
                
                if result.get('success'):
                    return Response({
                        "success": True,
                        "message": "پرداخت با موفقیت انجام شد",
                        "payment_id": payment.id,
                        "ref_id": result.get('ref_id'),
                        "order_id": payment.order.id if payment.order else None
                    })
                else:
                    return Response({
                        "success": False,
                        "message": result.get('message', 'خطا در تایید پرداخت'),
                        "payment_id": payment.id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                logger.error(f"خطا در تایید پرداخت: {str(e)}")
                return Response(
                    {"error": "خطای سیستمی در تایید پرداخت"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPaymentsAPIView(APIView):
    """API پرداخت‌های کاربر"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """دریافت لیست پرداخت‌های کاربر جاری"""
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        
        # فیلتر بر اساس وضعیت
        status_param = request.query_params.get('status')
        if status_param:
            payments = payments.filter(status=status_param)
        
        # پرداخت‌های مربوط به یک سفارش خاص
        order_id = request.query_params.get('order_id')
        if order_id:
            payments = payments.filter(order__id=order_id)
        
        # محدود کردن تعداد نتایج
        limit = request.query_params.get('limit')
        if limit and limit.isdigit():
            payments = payments[:int(limit)]
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
