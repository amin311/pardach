from django.urls import path
from .views import PluginListCreateView, PluginDetailView, PluginToggleView

app_name = 'plugins'

urlpatterns = [
    # مسیرهای مربوط به افزونه‌ها
    path('', PluginListCreateView.as_view(), name='plugin-list-create'),
    path('<int:plugin_id>/', PluginDetailView.as_view(), name='plugin-detail'),
    path('<int:plugin_id>/toggle/', PluginToggleView.as_view(), name='plugin-toggle'),
] 