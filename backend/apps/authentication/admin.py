from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Role
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    """تنظیمات نمایش مدل CustomUser در پنل ادمین"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'current_role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'current_role')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'email', 'current_role')}),
        (_('دسترسی‌ها'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'current_role'),
        }),
    )
    
    ordering = ('username',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """تنظیمات نمایش مدل Role در پنل ادمین"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'permissions')}),
    )
