from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Business, BusinessUser, BusinessActivity
from .serializers import BusinessSerializer, BusinessUserSerializer, BusinessActivitySerializer
from drf_spectacular.utils import extend_schema
from apps.core.utils import log_error, validate_file_size, validate_file_format
from django.db.models import Q

class BusinessListCreateView(APIView):
    """لیست و ایجاد کسب‌وکارها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست کسب‌وکارها", responses={200: BusinessSerializer(many=True)})
    def get(self, request):
        try:
            if request.user.is_staff:
                businesses = Business.objects.all()
            else:
                businesses = Business.objects.filter(Q(owner=request.user) | Q(users__user=request.user)).distinct()
            
            status_filter = request.query_params.get('status')
            if status_filter:
                businesses = businesses.filter(status=status_filter)
                
            serializer = BusinessSerializer(businesses, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت لیست کسب‌وکارها", e)
            return Response({'error': 'خطا در دریافت اطلاعات کسب‌وکارها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد کسب‌وکار جدید", request=BusinessSerializer, responses={201: BusinessSerializer})
    def post(self, request):
        try:
            if 'logo' in request.FILES:
                request.FILES['logo'] = validate_file_size(request.FILES['logo'])
                request.FILES['logo'] = validate_file_format(request.FILES['logo'])
            
            serializer = BusinessSerializer(data=request.data)
            if serializer.is_valid():
                business = serializer.save(owner=request.user)
                # ایجاد کاربر کسب‌وکار با نقش مدیر برای مالک
                BusinessUser.objects.create(business=business, user=request.user, role='manager')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد کسب‌وکار", e)
            return Response({'error': 'خطا در ایجاد کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessDetailView(APIView):
    """جزئیات، ویرایش و حذف کسب‌وکار"""
    permission_classes = [IsAuthenticated]

    def get_business(self, business_id, user):
        try:
            business = Business.objects.get(id=business_id)
            
            # بررسی دسترسی کاربر
            if not user.is_staff and business.owner != user and not business.users.filter(user=user).exists():
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            return business, None
        except Business.DoesNotExist:
            return None, Response({'error': 'کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در دریافت کسب‌وکار", e)
            return None, Response({'error': 'خطا در دریافت اطلاعات کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="دریافت جزئیات کسب‌وکار", responses={200: BusinessSerializer})
    def get(self, request, business_id):
        business, error_response = self.get_business(business_id, request.user)
        if error_response:
            return error_response
            
        serializer = BusinessSerializer(business)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش کسب‌وکار", request=BusinessSerializer, responses={200: BusinessSerializer})
    def put(self, request, business_id):
        business, error_response = self.get_business(business_id, request.user)
        if error_response:
            return error_response
            
        # بررسی مجوز ویرایش (فقط مالک یا ادمین)
        if business.owner != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجوز ویرایش این کسب‌وکار را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            if 'logo' in request.FILES:
                request.FILES['logo'] = validate_file_size(request.FILES['logo'])
                request.FILES['logo'] = validate_file_format(request.FILES['logo'])
                
            serializer = BusinessSerializer(business, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ویرایش کسب‌وکار", e)
            return Response({'error': 'خطا در ویرایش کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف کسب‌وکار", responses={204: None})
    def delete(self, request, business_id):
        business, error_response = self.get_business(business_id, request.user)
        if error_response:
            return error_response
            
        # بررسی مجوز حذف (فقط مالک یا ادمین)
        if business.owner != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجوز حذف این کسب‌وکار را ندارید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            business.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("خطا در حذف کسب‌وکار", e)
            return Response({'error': 'خطا در حذف کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessUserListCreateView(APIView):
    """لیست و ایجاد کاربران کسب‌وکار"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست کاربران کسب‌وکار", responses={200: BusinessUserSerializer(many=True)})
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            
            # بررسی دسترسی
            if not request.user.is_staff and business.owner != request.user and not business.users.filter(user=request.user).exists():
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            users = BusinessUser.objects.filter(business=business)
            serializer = BusinessUserSerializer(users, many=True)
            return Response(serializer.data)
        except Business.DoesNotExist:
            return Response({'error': 'کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در دریافت کاربران کسب‌وکار", e)
            return Response({'error': 'خطا در دریافت اطلاعات کاربران کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد کاربر کسب‌وکار جدید", request=BusinessUserSerializer, responses={201: BusinessUserSerializer})
    def post(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            
            # بررسی مجوز ایجاد کاربر (فقط مالک یا ادمین)
            if business.owner != request.user and not request.user.is_staff:
                return Response({'error': 'شما مجوز اضافه کردن کاربر به این کسب‌وکار را ندارید'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = BusinessUserSerializer(data={**request.data, 'business_id': business_id})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Business.DoesNotExist:
            return Response({'error': 'کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در ایجاد کاربر کسب‌وکار", e)
            return Response({'error': 'خطا در ایجاد کاربر کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessUserDetailView(APIView):
    """جزئیات، ویرایش و حذف کاربر کسب‌وکار"""
    permission_classes = [IsAuthenticated]
    
    def get_business_user(self, business_id, pk, user):
        try:
            business_user = BusinessUser.objects.get(business_id=business_id, id=pk)
            business = business_user.business
            
            # بررسی دسترسی
            if not user.is_staff and business.owner != user and not business.users.filter(user=user, role='manager').exists():
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            return business_user, None
        except BusinessUser.DoesNotExist:
            return None, Response({'error': 'کاربر کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در دریافت کاربر کسب‌وکار", e)
            return None, Response({'error': 'خطا در دریافت اطلاعات کاربر کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(summary="دریافت جزئیات کاربر کسب‌وکار", responses={200: BusinessUserSerializer})
    def get(self, request, business_id, pk):
        business_user, error_response = self.get_business_user(business_id, pk, request.user)
        if error_response:
            return error_response
            
        serializer = BusinessUserSerializer(business_user)
        return Response(serializer.data)
    
    @extend_schema(summary="ویرایش کاربر کسب‌وکار", request=BusinessUserSerializer, responses={200: BusinessUserSerializer})
    def put(self, request, business_id, pk):
        business_user, error_response = self.get_business_user(business_id, pk, request.user)
        if error_response:
            return error_response
            
        try:
            serializer = BusinessUserSerializer(business_user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ویرایش کاربر کسب‌وکار", e)
            return Response({'error': 'خطا در ویرایش کاربر کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(summary="حذف کاربر کسب‌وکار", responses={204: None})
    def delete(self, request, business_id, pk):
        business_user, error_response = self.get_business_user(business_id, pk, request.user)
        if error_response:
            return error_response
            
        try:
            business_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error("خطا در حذف کاربر کسب‌وکار", e)
            return Response({'error': 'خطا در حذف کاربر کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BusinessActivityListView(APIView):
    """لیست فعالیت‌های کسب‌وکار"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست فعالیت‌های کسب‌وکار", responses={200: BusinessActivitySerializer(many=True)})
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            
            # بررسی دسترسی
            if not request.user.is_staff and business.owner != request.user and not business.users.filter(user=request.user).exists():
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            activities = BusinessActivity.objects.filter(business=business, is_active=True)
            
            # فیلتر بر اساس نوع فعالیت
            activity_type = request.query_params.get('activity_type')
            if activity_type:
                activities = activities.filter(activity_type=activity_type)
                
            serializer = BusinessActivitySerializer(activities, many=True)
            return Response(serializer.data)
        except Business.DoesNotExist:
            return Response({'error': 'کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("خطا در دریافت فعالیت‌های کسب‌وکار", e)
            return Response({'error': 'خطا در دریافت اطلاعات فعالیت‌های کسب‌وکار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
