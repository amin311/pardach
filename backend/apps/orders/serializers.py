from rest_framework import serializers
from .models import Order, OrderItem, OrderSection, GarmentDetails, OrderStage
from apps.core.utils import to_jalali
from apps.designs.models import Design
from apps.templates_app.models import UserTemplate
from apps.designs.serializers import DesignSerializer, PrintLocationSerializer
from apps.templates_app.serializers import UserTemplateSerializer
from apps.business.serializers import BusinessSerializer
from django.utils.translation import gettext_lazy as _
from django.db import transaction

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

class GarmentDetailsSerializer(serializers.ModelSerializer):
    """سریالایزر برای جزئیات لباس"""
    
    class Meta:
        model = GarmentDetails
        fields = [
            'id', 'length_cm', 'width_cm', 'sleeve_length_cm',
            'chest_cm', 'shoulder_cm', 'notes'
        ]

class OrderSectionSerializer(serializers.ModelSerializer):
    """سریالایزر برای بخش‌های سفارش"""
    location = PrintLocationSerializer(read_only=True)
    location_id = serializers.UUIDField(write_only=True)
    design = DesignSerializer(read_only=True)
    design_id = serializers.UUIDField(write_only=True)
    calculated_cost = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)
    
    class Meta:
        model = OrderSection
        fields = [
            'id', 'location', 'location_id', 'design', 'design_id',
            'is_inner_print', 'quantity', 'custom_width_cm', 'custom_height_cm',
            'special_instructions', 'calculated_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """اضافه کردن هزینه محاسبه شده"""
        data = super().to_representation(instance)
        data['calculated_cost'] = instance.calculate_cost()
        return data

    def validate(self, attrs):
        """اعتبارسنجی داده‌ها"""
        if attrs.get('custom_width_cm') and attrs.get('custom_height_cm'):
            if attrs['custom_width_cm'] <= 0 or attrs['custom_height_cm'] <= 0:
                raise serializers.ValidationError(_("ابعاد سفارشی باید بزرگتر از صفر باشند"))
        
        if attrs.get('quantity', 1) <= 0:
            raise serializers.ValidationError(_("تعداد باید بزرگتر از صفر باشد"))
            
        return attrs

class OrderStageSerializer(serializers.ModelSerializer):
    """سریالایزر برای مراحل سفارش"""
    stage_type_display = serializers.CharField(source='get_stage_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderStage
        fields = [
            'id', 'stage_type', 'stage_type_display', 'status', 'status_display',
            'started_at', 'finished_at', 'assigned_to', 'assigned_to_name',
            'notes', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_duration(self, obj):
        """محاسبه مدت زمان مرحله"""
        if obj.started_at and obj.finished_at:
            delta = obj.finished_at - obj.started_at
            return delta.total_seconds() / 3600  # بر حسب ساعت
        return None

class OrderSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای سفارش"""
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    # workshop_name = serializers.CharField(source='workshop.name', read_only=True)
    
    # Nested serializers
    items = OrderItemSerializer(many=True, read_only=True)
    sections = OrderSectionSerializer(many=True, required=False)
    garment_details = GarmentDetailsSerializer(required=False)
    stages = OrderStageSerializer(many=True, read_only=True)
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    garment_size_display = serializers.CharField(source='get_garment_size_display', read_only=True)
    print_type_display = serializers.CharField(source='get_print_type_display', read_only=True)
    fabric_type_display = serializers.CharField(source='get_fabric_type_display', read_only=True)
    
    # Calculated fields
    total_sections_cost = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'business', 'business_name',
            # 'workshop', 'workshop_name', 
            'status', 'status_display',
            'garment_size', 'garment_size_display', 'print_type', 'print_type_display',
            'custom_size_details', 'fabric_type', 'fabric_type_display',
            'fabric_color', 'fabric_material', 'fabric_weight', 'fabric_details',
            'total_price', 'deposit_amount', 'is_paid', 'delivery_date',
            'completed_at', 'customer_notes', 'internal_notes', 'notes',
            'items', 'sections', 'garment_details', 'stages',
            'total_sections_cost', 'completion_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer', 'total_price', 'completed_at', 
            'created_at', 'updated_at'
        ]

    def get_total_sections_cost(self, obj):
        """محاسبه مجموع هزینه بخش‌ها"""
        return sum(section.calculate_cost() for section in obj.sections.all())

    def get_completion_percentage(self, obj):
        """محاسبه درصد تکمیل سفارش"""
        stages = obj.stages.all()
        if not stages.exists():
            return 0
        
        completed_stages = stages.filter(status='completed').count()
        total_stages = stages.count()
        return round((completed_stages / total_stages) * 100, 2)

    @transaction.atomic
    def create(self, validated_data):
        """ایجاد سفارش با بخش‌ها و جزئیات"""
        sections_data = validated_data.pop('sections', [])
        garment_details_data = validated_data.pop('garment_details', None)
        
        # ایجاد سفارش
        order = Order.objects.create(**validated_data)
        
        # ایجاد بخش‌ها
        for section_data in sections_data:
            OrderSection.objects.create(order=order, **section_data)
        
        # ایجاد جزئیات لباس
        if garment_details_data:
            GarmentDetails.objects.create(order=order, **garment_details_data)
        
        # ایجاد مرحله اولیه
        OrderStage.objects.create(
            order=order,
            stage_type='order_received',
            status='completed',
            started_at=order.created_at,
            finished_at=order.created_at
        )
        
        # محاسبه قیمت کل
        order.calculate_total_price()
        
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        """به‌روزرسانی سفارش"""
        sections_data = validated_data.pop('sections', None)
        garment_details_data = validated_data.pop('garment_details', None)
        
        # به‌روزرسانی فیلدهای اصلی
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # به‌روزرسانی بخش‌ها
        if sections_data is not None:
            # حذف بخش‌های قدیمی
            instance.sections.all().delete()
            
            # ایجاد بخش‌های جدید
            for section_data in sections_data:
                OrderSection.objects.create(order=instance, **section_data)
        
        # به‌روزرسانی جزئیات لباس
        if garment_details_data is not None:
            garment_details, created = GarmentDetails.objects.get_or_create(
                order=instance,
                defaults=garment_details_data
            )
            if not created:
                for attr, value in garment_details_data.items():
                    setattr(garment_details, attr, value)
                garment_details.save()
        
        # محاسبه مجدد قیمت
        instance.calculate_total_price()
        
        return instance

    def validate(self, attrs):
        """اعتبارسنجی کلی سفارش"""
        # بررسی وجود حداقل یک بخش
        if 'sections' in attrs and not attrs['sections']:
            raise serializers.ValidationError(_("سفارش باید حداقل یک بخش داشته باشد"))
        
        # بررسی تاریخ تحویل
        if attrs.get('delivery_date'):
            from django.utils import timezone
            if attrs['delivery_date'] <= timezone.now().date():
                raise serializers.ValidationError(_("تاریخ تحویل باید در آینده باشد"))
        
        return attrs 