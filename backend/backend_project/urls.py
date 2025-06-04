"""
URL configuration for backend_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.main.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/', include('apps.authentication.urls')),
    
    # API Endpoints
    path('api/core/', include('apps.core.urls')),
    path('api/templates/', include('apps.templates_app.urls')),
    path('api/payment/', include('apps.payment.urls')),
    path('api/business/', include('apps.business.urls')),
    path('api/notification/', include('apps.notification.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/main/', include('apps.main.urls')),
    path('api/designs/', include('apps.designs.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/settings/', include('apps.settings.urls')),
    path('api/workshop/', include('apps.workshop.urls')),
    path('api/craft/', include('apps.craft.urls')),
    path('api/tender/', include('apps.tender.urls')),
    path('api/set-design/', include('apps.set_design.urls')),
    path('api/print-locations/', include('apps.print_locations.urls')),
    path('api/', include('apps.api.urls')),
]

# اضافه کردن URL های فایل‌های استاتیک و مدیا در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # اضافه کردن API documentation
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
