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
from apps.main.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
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
    path('api/', include('apps.api.urls')),
]
