from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
<<<<<<< HEAD
from apps.designs.models import PrintLocation
from apps.designs.serializers import PrintLocationSerializer

class PrintLocationListCreateView(generics.ListCreateAPIView):
    """API برای لیست و ایجاد محل‌های چاپ روی لباس"""
    queryset = PrintLocation.objects.filter(is_active=True)
    serializer_class = PrintLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PrintLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API برای مشاهده، ویرایش و حذف محل چاپ"""
    queryset = PrintLocation.objects.all()
    serializer_class = PrintLocationSerializer
=======
from .models import PrintCenter
from .serializers import PrintCenterSerializer

class PrintCenterListCreateView(generics.ListCreateAPIView):
    """API برای لیست و ایجاد مکان‌های چاپ"""
    queryset = PrintCenter.objects.filter(is_active=True)
    serializer_class = PrintCenterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """فیلتر کردن بر اساس شهر"""
        queryset = super().get_queryset()
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset

class PrintCenterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API برای مشاهده، ویرایش و حذف مکان چاپ"""
    queryset = PrintCenter.objects.all()
    serializer_class = PrintCenterSerializer
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """حذف منطقی محل چاپ"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
