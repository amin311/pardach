from rest_framework import serializers

class DashboardSummarySerializer(serializers.Serializer):
    """سریالایزر برای خلاصه داده‌های داشبورد"""
    order_count = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_count = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    unread_notifications = serializers.IntegerField()
    report_count = serializers.IntegerField()

class ChartDataSerializer(serializers.Serializer):
    """سریالایزر برای داده‌های نمودار"""
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.FloatField())
    type = serializers.CharField()
    title = serializers.CharField()

class DashboardResponseSerializer(serializers.Serializer):
    """سریالایزر برای پاسخ API داشبورد"""
    summary = DashboardSummarySerializer()
    charts = serializers.DictField(child=ChartDataSerializer())

class BusinessStatsSerializer(serializers.Serializer):
    total_businesses = serializers.IntegerField()
    active_businesses = serializers.IntegerField()
    user_businesses = serializers.IntegerField()

class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    user_orders = serializers.IntegerField()
    weekly_orders = serializers.IntegerField()

class DesignStatsSerializer(serializers.Serializer):
    total_designs = serializers.IntegerField()
    public_designs = serializers.IntegerField()
    user_designs = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_downloads = serializers.IntegerField()

class DashboardStatsSerializer(serializers.Serializer):
    business_stats = BusinessStatsSerializer()
    order_stats = OrderStatsSerializer()
    design_stats = DesignStatsSerializer()

class PaymentStatsSerializer(serializers.Serializer):
    """سریالایزر برای آمار جزئی پرداخت‌ها"""
    total = serializers.IntegerField()
    successful_count = serializers.IntegerField()
    by_status = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    total_amount = serializers.FloatField() 