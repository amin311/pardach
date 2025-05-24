from django.contrib import admin
from .models import (
    SystemSetting, SiteSetting, HomeBlock,
    Tender, Bid, Award, Business,
    Workshop, WorkshopTask, WorkshopReport
)
from django.utils.translation import gettext_lazy as _

try:
    # optional nicety for drag‑and‑drop ordering
    from adminsortable2.admin import SortableAdminMixin
    base_cls = SortableAdminMixin
except ImportError:
    base_cls = admin.ModelAdmin

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """تنظیمات نمایش مدل SystemSetting در پنل ادمین"""
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'description')
    list_filter = ('key',)
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """کلید فقط در حالت ویرایش، فقط خواندنی است"""
        if obj:  # در حالت ویرایش
            return ['key']
        return []

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key",)
    search_fields = ("key",)

@admin.register(HomeBlock)
class HomeBlockAdmin(base_cls):
    list_display = ("title", "type", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("type", "is_active")

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "customer", "status", "deadline", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "customer__email")

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "tender", "business", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("tender__title", "business__name")

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ("tender", "bid", "awarded_at")

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name", "owner__email")

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("name", "daily_capacity", "used_capacity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "manager__email")

@admin.register(WorkshopTask)
class WorkshopTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "workshop", "status", "quantity", "due_date")
    list_filter = ("status", "workshop")
    search_fields = ("title", "tender__title")

@admin.register(WorkshopReport)
class WorkshopReportAdmin(admin.ModelAdmin):
    list_display = ("task", "reporter", "progress", "created_at")
    list_filter = ("progress",)
    search_fields = ("task__title", "reporter__email")
