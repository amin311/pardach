from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def settings_root(request):
    """
    نمایش مسیرهای اصلی تنظیمات
    """
    return Response({
        'message': 'API تنظیمات سیستم'
    })
