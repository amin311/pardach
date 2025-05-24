from rest_framework import serializers
from .models import Order, OrderItem
from apps.core.utils import to_jalali
from apps.designs.models import Design
from apps.templates_app.models import UserTemplate
from apps.designs.serializers import DesignSerializer
from apps.templates_app.serializers import UserTemplateSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """سریالایزر برای آیتم‌های سفارش"""
    design = DesignSerializer(read_only=True)
    design_id = serializers.PrimaryKeyRelatedField(source='design', queryset=Design.objects.all(), required=False, allow_null=True, write_only=True)
    user_template = UserTemplateSerializer(read_only=True)
    user_template_id = serializers.PrimaryKeyRelatedField(source='user_template', queryset=UserTemplate.objects.all(), required=False, allow_null=True, write_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'design', 'design_id', 'user_template', 'user_template_id', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = ['price']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class OrderSerializer(serializers.ModelSerializer):
    """سریالایزر برای سفارش‌ها"""
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.ReadOnlyField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'notes', 'items', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['total_price', 'user']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at) 