from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def craft_root(request):
    """
    نمایش مسیرهای اصلی صنایع دستی
    """
    return Response({
        'message': 'API صنایع دستی و سفارشات خاص'
    })
