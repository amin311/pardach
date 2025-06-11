from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Business, EmployeeRole

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_type', 'owner')
    list_filter = ('business_type',)
    search_fields = ('name', 'owner__username')
    raw_id_fields = ('owner',)

@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'role', 'payment_type', 'is_active')
    list_filter = ('role', 'payment_type', 'is_active')
    search_fields = ('user__username', 'business__name')
    raw_id_fields = ('user', 'business')
