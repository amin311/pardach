from rest_framework import serializers
from .models import (
    SystemSetting, SiteSetting, HomeBlock,
    Tender, Bid, Award, Business,
    Workshop, WorkshopTask, WorkshopReport,
    Order, OrderStage, Transaction, SetDesign
)

class SystemSettingSerializer(serializers.ModelSerializer):
    """سریالایزر برای تنظیمات سیستم"""
    class Meta:
        model = SystemSetting
        fields = ['key', 'value', 'description']
        read_only_fields = ['key']  # کلید فقط خواندنی در ویرایش 

class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ['key', 'value']
        read_only_fields = ['key']

class HomeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBlock
        fields = ("id", "title", "type", "config", "order") 

class TenderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    class Meta:
        model = Tender
        fields = ("id", "title", "description", "deadline", "status", "customer", "customer_name", "created_at")
        read_only_fields = ("status", "customer", "created_at")

class BidSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)
    class Meta:
        model = Bid
        fields = ("id", "tender", "business", "business_name", "amount", "message", "status", "created_at")
        read_only_fields = ("status", "business", "created_at")

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ("tender", "bid", "awarded_at") 

class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = "__all__"
        read_only_fields = ("used_capacity",)

class WorkshopTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopTask
        fields = "__all__"
        read_only_fields = ("status", "created_at")

class WorkshopReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopReport
        fields = "__all__"
        read_only_fields = ("created_at",)

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ("id", "name", "owner")
        read_only_fields = ("owner",)

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    class Meta:
        model = Order
        fields = ("id", "tender", "customer", "customer_name", "total_price", "status", "created_at")
        read_only_fields = ("customer", "created_at")

class OrderStageSerializer(serializers.ModelSerializer):
    is_paid = serializers.BooleanField(read_only=True)
    class Meta:
        model = OrderStage
        fields = ("id", "order", "sequence", "name", "amount_due", "amount_paid", "is_paid", "due_date", "paid_at")
        read_only_fields = ("amount_paid", "is_paid", "paid_at")

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "order_stage", "amount", "provider", "external_id", "status", "created_at")
        read_only_fields = ("status", "created_at")

class SetDesignSerializer(serializers.ModelSerializer):
    designer_name = serializers.CharField(source="designer.get_full_name", read_only=True)
    order_code = serializers.CharField(source="order_stage.order.id", read_only=True)
    status_fa = serializers.SerializerMethodField()

    class Meta:
        model = SetDesign
        fields = (
            "id", "order_stage", "designer", "designer_name", "order_code",
            "design_file", "preview", "status", "status_fa", "description",
            "created_at", "updated_at"
        )
        read_only_fields = ("designer", "preview", "created_at", "updated_at")

    def get_status_fa(self, obj):
        status_map = {
            "SUBMITTED": "ارسال‌شده",
            "APPROVED": "تأیید‌شده",
            "REJECTED": "رد‌شده"
        }
        return status_map.get(obj.status, obj.status) 