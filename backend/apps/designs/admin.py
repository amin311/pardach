from django.contrib import admin
from .models import Tag, DesignCategory, Family, Design, FamilyDesignRequirement, DesignFamily
from django.utils.translation import gettext_lazy as _

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'designs_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DesignCategory)
class DesignCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'designs_count', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'tags', 'categories', 'is_active')}),
    )

@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'is_public', 'views_count', 'downloads_count')
    list_filter = ('status', 'is_public', 'categories')
    search_fields = ('title', 'description', 'designer__username')
    filter_horizontal = ('categories',)
    readonly_fields = ('views_count', 'downloads_count')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'designer', 'status', 'is_public', 'price')
        }),
        ('فایل‌ها', {
            'fields': ('file', 'preview_image')
        }),
        ('دسته‌بندی', {
            'fields': ('categories',)
        }),
        ('آمار', {
            'fields': ('views_count', 'downloads_count')
        }),
    )

@admin.register(FamilyDesignRequirement)
class FamilyDesignRequirementAdmin(admin.ModelAdmin):
    list_display = ('family', 'design_type', 'quantity', 'is_required', 'fulfilled_count', 'is_fulfilled')
    search_fields = ('family__name', 'design_type')
    list_filter = ('is_required', 'created_at')

@admin.register(DesignFamily)
class DesignFamilyAdmin(admin.ModelAdmin):
    list_display = ('design', 'family', 'position', 'created_at')
    search_fields = ('design__title', 'family__name')
    list_filter = ('created_at',)
