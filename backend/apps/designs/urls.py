from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'designs'

# ایجاد router برای ViewSet ها
router = DefaultRouter()
router.register(r'print-locations', views.PrintLocationViewSet, basename='print-locations')

urlpatterns = [
    # مسیرهای ViewSet ها
    path('', include(router.urls)),
    
    # مسیرهای APIView ها
    path('tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('categories/', views.DesignCategoryListCreateView.as_view(), name='category-list-create'),
    path('families/', views.FamilyListCreateView.as_view(), name='family-list-create'),
    path('designs/', views.DesignListCreateView.as_view(), name='design-list-create'),
    path('designs/<int:design_id>/', views.DesignDetailView.as_view(), name='design-detail'),
    path('batch-upload/', views.BatchUploadView.as_view(), name='batch-upload'),
] 