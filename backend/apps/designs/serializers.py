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
    category_ids = serializers.PrimaryKeyRelatedField(queryset=DesignCategory.objects.all(), source='categories', many=True, write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True)
    families = FamilySerializer(many=True, read_only=True)
    family_ids = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all(), source='families', many=True, write_only=True)
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
            'created_at', 'updated_at', 'thumbnail_preview', 'aspect_ratio'
        ]

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

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