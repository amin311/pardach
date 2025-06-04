from rest_framework import serializers
from .models import Tag, DesignCategory, Family, Design, FamilyDesignRequirement, DesignFamily
from apps.core.utils import to_jalali

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'designs_count']

class DesignCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = DesignCategory
        fields = ['id', 'name', 'slug', 'parent', 'description', 'icon', 'designs_count', 'children_count', 'full_path', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class FamilySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = ['id', 'name', 'slug', 'description', 'tags', 'categories', 'designs_count', 'is_active', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class DesignSerializer(serializers.ModelSerializer):
    categories = DesignCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(queryset=DesignCategory.objects.all(), source='categories', many=True, write_only=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False)
    
    # برای families باید از DesignFamily استفاده کنیم چون رابطه مستقیم نداریم
    families = serializers.SerializerMethodField()
    family_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    # برای svg_file از source='file' استفاده می‌کنیم
    svg_file = serializers.FileField(source='file', required=False)
    
    created_by = serializers.StringRelatedField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    thumbnail_preview = serializers.ReadOnlyField()

    class Meta:
        model = Design
        fields = [
            'id', 'title', 'slug', 'description', 'size', 'type', 'svg_file', 'product_image', 'thumbnail',
            'categories', 'category_ids', 'tags', 'tag_ids', 'families', 'family_ids', 'similar_designs',
            'width', 'height', 'status', 'view_count', 'download_count', 'created_by', 'is_public',
            'created_at', 'updated_at', 'thumbnail_preview', 'aspect_ratio', 'file', 'preview_image', 'price'
        ]
        
    def get_families(self, obj):
        # دریافت خانواده‌ها از طریق DesignFamily
        design_families = DesignFamily.objects.filter(design=obj)
        families = [df.family for df in design_families]
        return FamilySerializer(families, many=True).data

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

    def create(self, validated_data):
        # استخراج family_ids
        family_ids = validated_data.pop('family_ids', [])
        
        # ایجاد Design
        design = Design.objects.create(**validated_data)
        
        # ایجاد روابط با خانواده‌ها
        for family_id in family_ids:
            try:
                family = Family.objects.get(id=family_id)
                DesignFamily.objects.create(design=design, family=family)
            except Family.DoesNotExist:
                pass
                
        return design

    def update(self, instance, validated_data):
        # استخراج family_ids
        family_ids = validated_data.pop('family_ids', None)
        
        # بروزرسانی فیلدهای Design
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # بروزرسانی روابط با خانواده‌ها اگر ارسال شده باشد
        if family_ids is not None:
            # حذف روابط قبلی
            DesignFamily.objects.filter(design=instance).delete()
            
            # ایجاد روابط جدید
            for family_id in family_ids:
                try:
                    family = Family.objects.get(id=family_id)
                    DesignFamily.objects.create(design=instance, family=family)
                except Family.DoesNotExist:
                    pass
                    
        return instance

class FamilyDesignRequirementSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = FamilyDesignRequirement
        fields = ['id', 'family', 'design_type', 'quantity', 'description', 'is_required', 'fulfilled_count', 'is_fulfilled', 'created_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

class DesignFamilySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = DesignFamily
        fields = ['id', 'design', 'family', 'position', 'notes', 'created_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at) 