from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import PrintLocation
from .serializers import PrintLocationSerializer

class PrintLocationListCreateView(generics.ListCreateAPIView):
    """API برای لیست و ایجاد مکان‌های چاپ"""
    queryset = PrintLocation.objects.filter(is_active=True)
    serializer_class = PrintLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """فیلتر کردن بر اساس شهر"""
        queryset = super().get_queryset()
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset

class PrintLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API برای مشاهده، ویرایش و حذف مکان چاپ"""
    queryset = PrintLocation.objects.all()
    serializer_class = PrintLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """حذف منطقی مکان چاپ"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT) 