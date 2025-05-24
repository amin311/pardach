from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import SetDesign
from .serializers import (
    SetDesignSerializer, 
    SetDesignApproveSerializer,
    SetDesignPaymentSerializer
)
from apps.payment.models import DesignerPayment


class SetDesignViewSet(viewsets.ModelViewSet):
    queryset = SetDesign.objects.all()
    serializer_class = SetDesignSerializer
    
    def get_permissions(self):
        """
        تنظیم سطوح دسترسی بر اساس عملیات
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]  # بعداً بررسی می‌شود که آیا کاربر ست‌بند است یا نه
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        فیلتر کردن نتایج بر اساس کاربر
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # اگر کاربر مدیر سیستم است، همه رکوردها را ببیند
        if user.is_staff:
            return queryset
        
        # اگر کاربر ست‌بند است، فقط ست‌های خودش را ببیند
        if user.roles and "set_designer" in user.roles:
            return queryset.filter(designer=user)
        
        # مشتری فقط ست‌های سفارش خودش را ببیند
        return queryset.filter(order_item__order__user=user)
    
    def perform_create(self, serializer):
        """
        ایجاد رکورد جدید و تنظیم برخی فیلدها
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        بررسی دسترسی برای به‌روزرسانی
        """
        instance = self.get_object()
        user = self.request.user
        
        # تنها ست‌بند تخصیص داده شده می‌تواند وضعیت را تغییر دهد
        if instance.designer != user and not user.is_staff:
            if 'status' in serializer.validated_data:
                raise permissions.PermissionDenied("شما اجازه تغییر وضعیت این ست را ندارید")
        
        serializer.save()
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        تأیید یا رد ست‌بندی توسط مشتری یا چاپخانه
        """
        instance = self.get_object()
        serializer = SetDesignApproveSerializer(data=request.data)
        
        if serializer.is_valid():
            # بررسی دسترسی - فقط مشتری/چاپخانه
            if request.user != instance.order_item.order.user and not request.user.is_staff:
                return Response({"detail": "شما اجازه تأیید این ست را ندارید"}, 
                               status=status.HTTP_403_FORBIDDEN)
            
            # بررسی وضعیت فعلی
            if instance.status != 'pending_approval':
                return Response({"detail": "این ست در وضعیت انتظار تأیید نیست"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                if serializer.validated_data['approved']:
                    # تأیید ست
                    instance.status = 'completed'
                    instance.save(update_fields=['status'])
                    return Response({"detail": "ست‌بندی با موفقیت تأیید شد"})
                else:
                    # رد ست و ایجاد کامنت
                    instance.status = 'rejected'
                    instance.save(update_fields=['status'])
                    # اینجا می‌توانید کامنت را در مدل دیگری ذخیره کنید
                    return Response({"detail": "ست‌بندی رد شد و نظر شما ثبت گردید"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay_designer(self, request, pk=None):
        """
        پرداخت هزینه ست‌بندی به ست‌بند
        """
        instance = self.get_object()
        serializer = SetDesignPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            # بررسی دسترسی - فقط مشتری/مدیر
            if request.user != instance.order_item.order.user and not request.user.is_staff:
                return Response({"detail": "شما اجازه پرداخت برای این ست را ندارید"}, 
                               status=status.HTTP_403_FORBIDDEN)
            
            # بررسی وضعیت فعلی
            if instance.status != 'completed':
                return Response({"detail": "این ست هنوز تأیید نشده است"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            if instance.paid:
                return Response({"detail": "هزینه این ست قبلاً پرداخت شده است"}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # ایجاد رکورد پرداخت
                payment = DesignerPayment.objects.create(
                    set_design=instance,
                    designer=instance.designer,
                    amount=serializer.validated_data['amount'],
                    payment_method=serializer.validated_data['payment_method']
                )
                
                # به‌روزرسانی وضعیت پرداخت
                instance.paid = True
                instance.save(update_fields=['paid'])
                
                return Response({
                    "detail": "پرداخت با موفقیت انجام شد",
                    "payment_id": payment.id
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 