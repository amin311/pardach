from rest_framework import serializers
from .models import Payment, Transaction
from apps.orders.models import Order
import jdatetime


class TransactionSerializer(serializers.ModelSerializer):
    """سریالایزر مدل تراکنش"""
    created_at_jalali = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'payment', 'amount', 'status', 'authority', 
            'ref_id', 'gateway_response', 'created_at', 'created_at_jalali'
        ]
        read_only_fields = ['id', 'created_at', 'created_at_jalali']
    
    def get_created_at_jalali(self, obj):
        """تبدیل تاریخ ایجاد به شمسی"""
        return obj.jalali_created_at()


class PaymentSerializer(serializers.ModelSerializer):
    """سریالایزر مدل پرداخت"""
    transactions = TransactionSerializer(many=True, read_only=True)
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    order_code = serializers.SerializerMethodField()
    order_id = serializers.PrimaryKeyRelatedField(
        source='order',
        queryset=Order.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_display', 'order', 'order_id', 'order_code',
            'amount', 'status', 'transaction_id', 'gateway',
            'callback_url', 'description', 'payment_data',
            'transactions', 'created_at', 'updated_at',
            'created_at_jalali', 'updated_at_jalali'
        ]
        read_only_fields = [
            'id', 'user', 'user_display', 'transaction_id',
            'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali'
        ]
    
    def get_created_at_jalali(self, obj):
        """تبدیل تاریخ ایجاد به شمسی"""
        return obj.jalali_created_at()
    
    def get_updated_at_jalali(self, obj):
        """تبدیل تاریخ بروزرسانی به شمسی"""
        return obj.jalali_updated_at()
    
    def get_user_display(self, obj):
        """نمایش نام کاربر"""
        if hasattr(obj.user, 'get_full_name') and obj.user.get_full_name():
            return obj.user.get_full_name()
        return obj.user.username
    
    def get_order_code(self, obj):
        """نمایش شناسه کوتاه سفارش"""
        return str(obj.order.id)[:8] if obj.order else None
    
    def validate_order_id(self, order):
        """اعتبارسنجی سفارش"""
        # بررسی وجود پرداخت موفق برای سفارش
        existing_payment = Payment.objects.filter(
            order=order,
            status='successful'
        ).exists()
        
        if existing_payment:
            raise serializers.ValidationError("این سفارش قبلاً پرداخت شده است")
        
        return order
    
    def create(self, validated_data):
        """ایجاد پرداخت جدید"""
        # استخراج کاربر از درخواست
        request = self.context.get('request')
        user = request.user if request else None
        
        # اضافه کردن کاربر به داده‌ها
        validated_data['user'] = user
        
        return super().create(validated_data)


class PaymentRequestSerializer(serializers.Serializer):
    """سریالایزر درخواست پرداخت"""
    order_id = serializers.UUIDField(required=True)
    gateway = serializers.ChoiceField(
        choices=Payment.GATEWAY_CHOICES,
        default='zarinpal'
    )
    callback_url = serializers.URLField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_order_id(self, order_id):
        """اعتبارسنجی سفارش"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError("سفارش مورد نظر یافت نشد")
        
        # بررسی وجود پرداخت موفق برای سفارش
        existing_payment = Payment.objects.filter(
            order=order,
            status='successful'
        ).exists()
        
        if existing_payment:
            raise serializers.ValidationError("این سفارش قبلاً پرداخت شده است")
        
        return order_id


class PaymentVerifySerializer(serializers.Serializer):
    """سریالایزر تایید پرداخت"""
    authority = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    id_pay_id = serializers.CharField(required=False) 