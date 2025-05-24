from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status, viewsets, mixins, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser
from .models import SystemSetting, SiteSetting, HomeBlock, Tender, Bid, Award, Business, Workshop, WorkshopTask, WorkshopReport, Order, OrderStage, Transaction, SetDesign
from .serializers import SystemSettingSerializer, HomeBlockSerializer, TenderSerializer, BidSerializer, AwardSerializer, BusinessSerializer, WorkshopSerializer, WorkshopTaskSerializer, WorkshopReportSerializer, SiteSettingSerializer, OrderSerializer, OrderStageSerializer, TransactionSerializer, SetDesignSerializer
from .utils import log_error

# Create your views here.

class SystemSettingView(APIView):
    """API برای مدیریت تنظیمات سیستمی"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """دریافت لیست تمام تنظیمات سیستمی"""
        try:
            settings = SystemSetting.objects.all()
            serializer = SystemSettingSerializer(settings, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving system settings", e)
            return Response({'error': 'خطا در دریافت تنظیمات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """ایجاد یک تنظیم سیستمی جدید"""
        try:
            serializer = SystemSettingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating system setting", e)
            return Response({'error': 'خطا در ایجاد تنظیم'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, key):
        """به‌روزرسانی یک تنظیم سیستمی بر اساس کلید آن"""
        try:
            setting = SystemSetting.objects.get(key=key)
            serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SystemSetting.DoesNotExist:
            return Response({'error': 'تنظیم یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating system setting", e)
            return Response({'error': 'خطا در به‌روزرسانی تنظیم'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([AllowAny])
def public_home(request):
    """Return global toggle + active home blocks; no auth required."""
    setting = SiteSetting.objects.filter(key="require_signup_for_home").first()
    require_signup = bool(setting and setting.value.get("require_signup_for_home", False))

    blocks_qs = HomeBlock.objects.filter(is_active=True).order_by("order")
    data = {
        "require_signup": require_signup,
        "blocks": HomeBlockSerializer(blocks_qs, many=True).data,
    }
    return Response(data)

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == "customer"

class IsBusiness(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == "business"

class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsCustomer()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.select_related("tender", "business")
    serializer_class = BidSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsAuthenticated(), IsBusiness()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        business = self.request.user.business  # assuming One‑To‑One
        serializer.save(business=business)

class AwardViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Award.objects.select_related("tender", "bid")
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated]

class WorkshopViewSet(viewsets.ModelViewSet):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Workshop.objects.all()
        return Workshop.objects.filter(manager=self.request.user)

class WorkshopTaskViewSet(viewsets.ModelViewSet):
    queryset = WorkshopTask.objects.all()
    serializer_class = WorkshopTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return WorkshopTask.objects.all()
        return WorkshopTask.objects.filter(workshop__manager=self.request.user)

class WorkshopReportViewSet(viewsets.ModelViewSet):
    queryset = WorkshopReport.objects.all()
    serializer_class = WorkshopReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return WorkshopReport.objects.all()
        return WorkshopReport.objects.filter(reporter=self.request.user)

class SystemSettingViewSet(viewsets.ModelViewSet):
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAdminUser]

class SiteSettingViewSet(viewsets.ModelViewSet):
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer
    permission_classes = [permissions.IsAdminUser]

class HomeBlockViewSet(viewsets.ModelViewSet):
    queryset = HomeBlock.objects.all()
    serializer_class = HomeBlockSerializer
    permission_classes = [permissions.IsAdminUser]

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Business.objects.all()
        return Business.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class OrderStageViewSet(viewsets.ModelViewSet):
    queryset = OrderStage.objects.all()
    serializer_class = OrderStageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderStage.objects.all()
        return OrderStage.objects.filter(order__customer=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(order_stage__order__customer=self.request.user)

class IsDesignerSet(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "designer_set"

class SetDesignViewSet(viewsets.ModelViewSet):
    queryset = SetDesign.objects.all()
    serializer_class = SetDesignSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated & (IsDesignerSet | permissions.IsAdminUser)]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SetDesign.objects.all()
        return SetDesign.objects.filter(designer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(designer=self.request.user)

    @action(detail=True, methods=["patch"])
    def upload(self, request, pk=None):
        instance = self.get_object()
        if "design_file" not in request.FILES:
            return Response(
                {"error": "فایل طراحی ارسال نشده است"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.design_file = request.FILES["design_file"]
        instance.status = SetDesign.SUBMITTED
        instance.save()
        
        return Response(SetDesignSerializer(instance).data)
