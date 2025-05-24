from rest_framework import serializers
from .models import Template, Section, DesignInput, Condition, UserTemplate, UserSection, UserDesignInput, UserCondition, SetDimensions
from apps.core.utils import to_jalali
from apps.designs.models import Tag, DesignCategory, Design
from apps.designs.serializers import TagSerializer, DesignCategorySerializer, DesignSerializer

class TemplateSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False)
    categories = DesignCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(queryset=DesignCategory.objects.all(), source='categories', many=True, write_only=True, required=False)
    created_by = serializers.StringRelatedField(source='creator')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    thumbnail_preview = serializers.ReadOnlyField()

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'slug', 'title', 'description', 'price', 'discount_price', 'discount_percent',
            'status', 'is_premium', 'is_featured', 'view_count', 'usage_count', 'preview_image', 'thumbnail',
            'tags', 'tag_ids', 'categories', 'category_ids', 'similar_templates', 'created_by',
            'created_at', 'updated_at', 'thumbnail_preview'
        ]

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class SectionSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id', 'template', 'name', 'slug', 'description', 'order', 'is_required',
            'unlimited_design_inputs', 'max_design_inputs', 'preview_image', 'created_at', 'updated_at'
        ]

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class DesignInputSerializer(serializers.ModelSerializer):
    default_design = DesignSerializer(read_only=True)
    default_design_id = serializers.PrimaryKeyRelatedField(queryset=Design.objects.all(), source='default_design', write_only=True, required=False)
    allowed_designs = DesignSerializer(many=True, read_only=True)
    allowed_design_ids = serializers.PrimaryKeyRelatedField(queryset=Design.objects.all(), source='allowed_designs', many=True, write_only=True, required=False)
    allowed_categories = DesignCategorySerializer(many=True, read_only=True)
    allowed_category_ids = serializers.PrimaryKeyRelatedField(queryset=DesignCategory.objects.all(), source='allowed_categories', many=True, write_only=True, required=False)
    allowed_tags = TagSerializer(many=True, read_only=True)
    allowed_tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), source='allowed_tags', many=True, write_only=True, required=False)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = DesignInput
        fields = [
            'id', 'section', 'name', 'description', 'order', 'is_required', 'default_design', 'default_design_id',
            'allowed_designs', 'allowed_design_ids', 'allowed_categories', 'allowed_category_ids', 
            'allowed_tags', 'allowed_tag_ids', 'min_width', 'min_height',
            'max_width', 'max_height', 'created_at', 'updated_at'
        ]

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class ConditionSerializer(serializers.ModelSerializer):
    options_list = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Condition
        fields = [
            'id', 'section', 'name', 'description', 'condition_type', 'options', 'options_list', 'default_value',
            'is_required', 'order', 'affects_pricing', 'price_factor', 'created_at', 'updated_at'
        ]
    
    def get_options_list(self, obj):
        return obj.get_options_list()

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class UserTemplateSerializer(serializers.ModelSerializer):
    template = TemplateSerializer(read_only=True)
    template_id = serializers.PrimaryKeyRelatedField(queryset=Template.objects.all(), source='template', write_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = UserTemplate
        fields = ['id', 'user', 'template', 'template_id', 'name', 'description', 'is_completed', 'final_price', 'unique_id', 'created_at', 'updated_at']
        read_only_fields = ['user', 'final_price', 'unique_id']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        user_template = super().create(validated_data)
        
        # ایجاد بخش‌های کاربر براساس بخش‌های قالب
        template = validated_data['template']
        for section in template.sections.all():
            user_section = UserSection.objects.create(
                user_template=user_template,
                section=section
            )
            
            # ایجاد ورودی‌های طرح کاربر براساس ورودی‌های طرح بخش
            for i, design_input in enumerate(section.design_inputs.all()):
                UserDesignInput.objects.create(
                    user_section=user_section,
                    design_input=design_input,
                    design=design_input.default_design,
                    order=i+1
                )
            
            # ایجاد شرایط کاربر براساس شرایط بخش
            for condition in section.conditions.all():
                UserCondition.objects.create(
                    user_section=user_section,
                    condition=condition,
                    value=condition.default_value
                )
                
        return user_template

class UserSectionSerializer(serializers.ModelSerializer):
    section = SectionSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    user_design_inputs = serializers.SerializerMethodField()
    user_conditions = serializers.SerializerMethodField()

    class Meta:
        model = UserSection
        fields = ['id', 'user_template', 'section', 'is_completed', 'user_design_inputs', 'user_conditions', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)
        
    def get_user_design_inputs(self, obj):
        return UserDesignInputSerializer(obj.user_design_inputs.all(), many=True).data
        
    def get_user_conditions(self, obj):
        return UserConditionSerializer(obj.user_conditions.all(), many=True).data

class UserDesignInputSerializer(serializers.ModelSerializer):
    design = DesignSerializer(read_only=True)
    design_id = serializers.PrimaryKeyRelatedField(queryset=Design.objects.all(), source='design', write_only=True, required=False, allow_null=True)
    design_input = DesignInputSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = UserDesignInput
        fields = ['id', 'user_section', 'design_input', 'design', 'design_id', 'order', 'created_at', 'updated_at']
        read_only_fields = ['user_section', 'design_input', 'order']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class UserConditionSerializer(serializers.ModelSerializer):
    condition = ConditionSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = UserCondition
        fields = ['id', 'user_section', 'condition', 'value', 'created_at', 'updated_at']
        read_only_fields = ['user_section', 'condition']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class SetDimensionsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = SetDimensions
        fields = ['id', 'name', 'width', 'height', 'created_at', 'updated_at']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at) 