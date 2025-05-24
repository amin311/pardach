from django.urls import path
from .views import (
    TemplateListCreateView, TemplateDetailView,
    SectionListCreateView, SectionDetailView,
    UserTemplateListCreateView, UserTemplateDetailView,
    UserSectionListView, UserSectionDetailView,
    UserDesignInputDetailView, UserConditionDetailView,
    SetDimensionsListCreateView, SetDimensionsDetailView
)

urlpatterns = [
    # مسیرهای مربوط به قالب‌ها
    path('templates/', TemplateListCreateView.as_view(), name='template_list_create'),
    path('templates/<str:template_id>/', TemplateDetailView.as_view(), name='template_detail'),
    
    # مسیرهای مربوط به بخش‌ها
    path('templates/<str:template_id>/sections/', SectionListCreateView.as_view(), name='section_list_create'),
    path('sections/<str:section_id>/', SectionDetailView.as_view(), name='section_detail'),
    
    # مسیرهای مربوط به قالب‌های کاربر
    path('user-templates/', UserTemplateListCreateView.as_view(), name='user_template_list_create'),
    path('user-templates/<str:user_template_id>/', UserTemplateDetailView.as_view(), name='user_template_detail'),
    
    # مسیرهای مربوط به بخش‌های کاربر
    path('user-templates/<str:user_template_id>/sections/', UserSectionListView.as_view(), name='user_section_list'),
    path('user-sections/<str:user_section_id>/', UserSectionDetailView.as_view(), name='user_section_detail'),
    
    # مسیرهای مربوط به ورودی‌های طرح کاربر
    path('user-design-inputs/<str:user_design_input_id>/', UserDesignInputDetailView.as_view(), name='user_design_input_detail'),
    
    # مسیرهای مربوط به شرایط کاربر
    path('user-conditions/<str:user_condition_id>/', UserConditionDetailView.as_view(), name='user_condition_detail'),
    
    # مسیرهای مربوط به ابعاد ست
    path('set-dimensions/', SetDimensionsListCreateView.as_view(), name='set_dimensions_list_create'),
    path('set-dimensions/<str:set_dimensions_id>/', SetDimensionsDetailView.as_view(), name='set_dimensions_detail'),
] 