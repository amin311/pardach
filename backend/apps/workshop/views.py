from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def workshop_root(request):
    """
    نمایش مسیرهای اصلی کارگاه
    """
    return Response({
        'message': 'API کارگاه و سفارشات سفارشی'
    })
