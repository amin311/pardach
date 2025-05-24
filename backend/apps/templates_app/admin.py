from django.contrib import admin
from .models import Template, Section, DesignInput, Condition, UserTemplate, UserSection, UserDesignInput, UserCondition, SetDimensions
from django.utils.translation import gettext_lazy as _

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'slug', 'creator', 'status', 'is_premium', 'is_featured', 'view_count', 'created_at')
    search_fields = ('title', 'name', 'description')
    list_filter = ('status', 'is_premium', 'is_featured', 'created_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'title', 'description', 'price', 'discount_price', 'discount_percent', 'status', 'is_premium', 'is_featured')}),
        (_('تصاویر'), {'fields': ('preview_image', 'thumbnail', 'thumbnail_preview')}),
        (_('ارتباطات'), {'fields': ('creator', 'tags', 'categories', 'similar_templates')}),
        (_('آمار'), {'fields': ('view_count', 'usage_count')}),
    )
    readonly_fields = ('thumbnail_preview', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'order', 'is_required', 'created_at')
    search_fields = ('name', 'description', 'template__name')
    list_filter = ('is_required', 'created_at')
    fieldsets = (
        (None, {'fields': ('template', 'name', 'slug', 'description', 'order', 'is_required', 'unlimited_design_inputs', 'max_design_inputs')}),
        (_('تصاویر'), {'fields': ('preview_image',)}),
    )
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DesignInput)
class DesignInputAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'order', 'is_required', 'created_at')
    search_fields = ('name', 'description', 'section__name')
    list_filter = ('is_required', 'created_at')
    fieldsets = (
        (None, {'fields': ('section', 'name', 'description', 'order', 'is_required')}),
        (_('طرح‌ها'), {'fields': ('default_design', 'allowed_designs', 'allowed_categories', 'allowed_tags')}),
        (_('ابعاد'), {'fields': ('min_width', 'min_height', 'max_width', 'max_height')}),
    )

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'condition_type', 'is_required', 'affects_pricing', 'order', 'created_at')
    search_fields = ('name', 'description', 'section__name')
    list_filter = ('condition_type', 'is_required', 'affects_pricing', 'created_at')
    fieldsets = (
        (None, {'fields': ('section', 'name', 'description', 'condition_type', 'options', 'default_value', 'is_required', 'order')}),
        (_('قیمت‌گذاری'), {'fields': ('affects_pricing', 'price_factor')}),
    )

@admin.register(UserTemplate)
class UserTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'template', 'is_completed', 'final_price', 'created_at')
    search_fields = ('name', 'user__username', 'template__name')
    list_filter = ('is_completed', 'created_at')
    fieldsets = (
        (None, {'fields': ('user', 'template', 'name', 'description', 'is_completed', 'final_price', 'unique_id')}),
    )
    readonly_fields = ('unique_id', 'created_at', 'updated_at')

@admin.register(UserSection)
class UserSectionAdmin(admin.ModelAdmin):
    list_display = ('user_template', 'section', 'is_completed', 'created_at')
    search_fields = ('user_template__name', 'section__name')
    list_filter = ('is_completed', 'created_at')

@admin.register(UserDesignInput)
class UserDesignInputAdmin(admin.ModelAdmin):
    list_display = ('user_section', 'design_input', 'design', 'order', 'created_at')
    search_fields = ('user_section__section__name', 'design_input__name', 'design__title')
    list_filter = ('created_at',)

@admin.register(UserCondition)
class UserConditionAdmin(admin.ModelAdmin):
    list_display = ('user_section', 'condition', 'value', 'created_at')
    search_fields = ('user_section__section__name', 'condition__name', 'value')
    list_filter = ('created_at',)

@admin.register(SetDimensions)
class SetDimensionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
