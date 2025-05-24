from django.contrib import admin
from .models import Business, BusinessUser
from django.utils.translation import gettext_lazy as _

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'description', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'role')
    list_filter = ('role', 'business')
    search_fields = ('user__username', 'business__name')
