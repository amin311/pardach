from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from .models import Tender, TenderBid
from .serializers import TenderSerializer, TenderBidSerializer
from apps.core.utils import log_error

# Create your views here.

@api_view(['GET'])
def tender_root(request):
    """
    نمایش مسیرهای اصلی مناقصه‌ها
    """
    return Response({
        'message': 'API مناقصه‌ها و درخواست‌های قیمت'
    })

class TenderListCreateView(APIView):
    """API برای نمایش لیست مناقصه‌ها و ایجاد مناقصه جدید"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست مناقصه‌ها", responses={200: TenderSerializer(many=True)})
    def get(self, request):
        try:
            # فیلترهای پایه
            tenders = Tender.objects.all()
            
            # فیلتر بر اساس نوع مناقصه
            tender_type = request.query_params.get('type')
            if tender_type:
                tenders = tenders.filter(tender_type=tender_type)
            
            # فیلتر بر اساس وضعیت
            status = request.query_params.get('status')
            if status:
                tenders = tenders.filter(status=status)
            
            # فیلتر مناقصه‌های باز (deadline نگذشته)
            if request.query_params.get('open_only') == 'true':
                tenders = tenders.filter(
                    Q(status='open') & Q(deadline__gt=timezone.now())
                )
            
            # جستجو
            search = request.query_params.get('search')
            if search:
                tenders = tenders.filter(
                    Q(title__icontains=search) | 
                    Q(description__icontains=search)
                )
            
            serializer = TenderSerializer(tenders, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving tenders", e)
            return Response(
                {'error': 'خطا در دریافت لیست مناقصه‌ها'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="ایجاد مناقصه جدید", request=TenderSerializer, responses={201: TenderSerializer})
    def post(self, request):
        try:
            serializer = TenderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating tender", e)
            return Response(
                {'error': 'خطا در ایجاد مناقصه'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TenderDetailView(APIView):
    """API برای نمایش، ویرایش و حذف مناقصه"""
    permission_classes = [IsAuthenticated]

    def get_tender(self, tender_id):
        try:
            return Tender.objects.get(id=tender_id)
        except Tender.DoesNotExist:
            return None

    @extend_schema(summary="دریافت جزئیات مناقصه", responses={200: TenderSerializer})
    def get(self, request, tender_id):
        tender = self.get_tender(tender_id)
        if not tender:
            return Response(
                {'error': 'مناقصه یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenderSerializer(tender)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش مناقصه", request=TenderSerializer, responses={200: TenderSerializer})
    def put(self, request, tender_id):
        tender = self.get_tender(tender_id)
        if not tender:
            return Response(
                {'error': 'مناقصه یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # فقط ایجاد کننده یا ادمین می‌تواند ویرایش کند
        if tender.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'دسترسی غیرمجاز'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            serializer = TenderSerializer(tender, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error updating tender", e)
            return Response(
                {'error': 'خطا در به‌روزرسانی مناقصه'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="حذف مناقصه")
    def delete(self, request, tender_id):
        tender = self.get_tender(tender_id)
        if not tender:
            return Response(
                {'error': 'مناقصه یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # فقط ایجاد کننده یا ادمین می‌تواند حذف کند
        if tender.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'دسترسی غیرمجاز'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            tender.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("Error deleting tender", e)
            return Response(
                {'error': 'خطا در حذف مناقصه'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TenderBidListCreateView(APIView):
    """API برای نمایش و ثبت پیشنهاد برای مناقصه"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست پیشنهادها", responses={200: TenderBidSerializer(many=True)})
    def get(self, request, tender_id):
        try:
            tender = Tender.objects.get(id=tender_id)
            # فقط ایجاد کننده مناقصه یا صاحب پیشنهاد می‌تواند پیشنهادها را ببیند
            if tender.created_by != request.user and not request.user.is_staff:
                bids = tender.bids.filter(business__owner=request.user)
            else:
                bids = tender.bids.all()
            
            serializer = TenderBidSerializer(bids, many=True)
            return Response(serializer.data)
        except Tender.DoesNotExist:
            return Response(
                {'error': 'مناقصه یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_error("Error retrieving tender bids", e)
            return Response(
                {'error': 'خطا در دریافت پیشنهادها'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="ثبت پیشنهاد جدید", request=TenderBidSerializer, responses={201: TenderBidSerializer})
    def post(self, request, tender_id):
        try:
            tender = Tender.objects.get(id=tender_id)
            
            # بررسی مهلت مناقصه
            if tender.deadline < timezone.now():
                return Response(
                    {'error': 'مهلت ارسال پیشنهاد به پایان رسیده است'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # بررسی وضعیت مناقصه
            if tender.status != 'open':
                return Response(
                    {'error': 'مناقصه در وضعیت باز نیست'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = TenderBidSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(tender=tender)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tender.DoesNotExist:
            return Response(
                {'error': 'مناقصه یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            log_error("Error creating tender bid", e)
            return Response(
                {'error': 'خطا در ثبت پیشنهاد'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TenderBidDetailView(APIView):
    """API برای نمایش، ویرایش و حذف پیشنهاد مناقصه"""
    permission_classes = [IsAuthenticated]

    def get_bid(self, tender_id, bid_id):
        try:
            return TenderBid.objects.get(tender_id=tender_id, id=bid_id)
        except TenderBid.DoesNotExist:
            return None

    @extend_schema(summary="دریافت جزئیات پیشنهاد", responses={200: TenderBidSerializer})
    def get(self, request, tender_id, bid_id):
        bid = self.get_bid(tender_id, bid_id)
        if not bid:
            return Response(
                {'error': 'پیشنهاد یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # بررسی دسترسی
        if bid.business.owner != request.user and bid.tender.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'دسترسی غیرمجاز'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TenderBidSerializer(bid)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش پیشنهاد", request=TenderBidSerializer, responses={200: TenderBidSerializer})
    def put(self, request, tender_id, bid_id):
        bid = self.get_bid(tender_id, bid_id)
        if not bid:
            return Response(
                {'error': 'پیشنهاد یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # فقط صاحب پیشنهاد می‌تواند ویرایش کند
        if bid.business.owner != request.user:
            return Response(
                {'error': 'دسترسی غیرمجاز'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # بررسی مهلت مناقصه
        if bid.tender.deadline < timezone.now():
            return Response(
                {'error': 'مهلت ویرایش پیشنهاد به پایان رسیده است'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = TenderBidSerializer(bid, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error updating tender bid", e)
            return Response(
                {'error': 'خطا در به‌روزرسانی پیشنهاد'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(summary="حذف پیشنهاد")
    def delete(self, request, tender_id, bid_id):
        bid = self.get_bid(tender_id, bid_id)
        if not bid:
            return Response(
                {'error': 'پیشنهاد یافت نشد'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # فقط صاحب پیشنهاد می‌تواند حذف کند
        if bid.business.owner != request.user:
            return Response(
                {'error': 'دسترسی غیرمجاز'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            bid.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("Error deleting tender bid", e)
            return Response(
                {'error': 'خطا در حذف پیشنهاد'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
