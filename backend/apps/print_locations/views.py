from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """حذف منطقی مکان چاپ"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
