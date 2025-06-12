from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """حذف منطقی محل چاپ"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT) 