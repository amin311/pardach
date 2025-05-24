from rest_framework import serializers
from .models import Promotion, MainPageSetting

class SummaryItemSerializer(serializers.Serializer):
    """سریالایزر برای آیتم‌های خلاصه در صفحه اصلی"""
    id = serializers.CharField()
    title = serializers.CharField(required=False)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    status = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    is_read = serializers.BooleanField(required=False)
    read = serializers.BooleanField(required=False)
    link = serializers.CharField(required=False)
    image = serializers.CharField(required=False)
    created_at = serializers.CharField()

class PromotionSerializer(serializers.ModelSerializer):
    """سریالایزر برای تبلیغات در صفحه اصلی"""
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'image', 'link', 'order']

class MainPageSettingSerializer(serializers.ModelSerializer):
    """سریالایزر برای تنظیمات صفحه اصلی"""
    class Meta:
        model = MainPageSetting
        fields = ['key', 'value', 'description', 'is_active']

class NavigationSerializer(serializers.Serializer):
    """سریالایزر برای آیتم‌های منوی ناوبری"""
    title = serializers.CharField()
    icon = serializers.CharField()
    link = serializers.CharField()
    visible = serializers.BooleanField()

class MainPageSummarySerializer(serializers.Serializer):
    """سریالایزر برای خلاصه داده‌های صفحه اصلی"""
    order_count = serializers.IntegerField()
    payment_count = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    recent_orders = SummaryItemSerializer(many=True)
    recent_payments = SummaryItemSerializer(many=True)
    recent_notifications = SummaryItemSerializer(many=True)
    recent_chats = SummaryItemSerializer(many=True)
    recent_designs = SummaryItemSerializer(many=True)

class WelcomeDataSerializer(serializers.Serializer):
    """سریالایزر برای داده‌های خوش‌آمدگویی"""
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    today_date_jalali = serializers.CharField(required=False)
    last_login_jalali = serializers.CharField(required=False)
    unread_count = serializers.IntegerField(required=False)
    order_in_progress = serializers.IntegerField(required=False)

class MainPageResponseSerializer(serializers.Serializer):
    """سریالایزر اصلی برای پاسخ API صفحه اصلی"""
    summary = MainPageSummarySerializer()
    promotions = PromotionSerializer(many=True)
    navigation = NavigationSerializer(many=True)
    welcome_data = WelcomeDataSerializer(required=False) 