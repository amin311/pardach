from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Tender, TenderBid

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ('title', 'tender_type', 'status', 'created_by', 'deadline', 'winner', 'created_at')
    list_filter = ('tender_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'created_by__username', 'winner__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'tender_type', 'status', 'created_by')
        }),
        (_('زمان‌بندی و بودجه'), {
            'fields': ('deadline', 'budget_min', 'budget_max')
        }),
        (_('نیازمندی‌ها'), {
            'fields': ('required_design_count', 'required_print_count', 'requirements', 'attachments')
        }),
        (_('نتیجه'), {
            'fields': ('winner', 'winning_bid')
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'winner', 'winning_bid')

@admin.register(TenderBid)
class TenderBidAdmin(admin.ModelAdmin):
    list_display = ('tender', 'business', 'proposed_price', 'delivery_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tender__title', 'business__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('tender', 'business', 'status')
        }),
        (_('پیشنهاد'), {
            'fields': ('proposed_price', 'delivery_time', 'description', 'attachments')
        }),
        (_('طرح‌ها'), {
            'fields': ('proposed_designs',)
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tender', 'business')
