from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.utils import log_error

class RegisterView(APIView):
    """API برای ثبت‌نام کاربر جدید"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error registering user", e)
            return Response({'error': 'خطا در ثبت‌نام'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """API برای ورود کاربر و دریافت توکن‌ها"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error logging in user", e)
            return Response({'error': 'خطا در ورود'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListCreateView(APIView):
    """API برای مشاهده لیست کاربران و ایجاد کاربر جدید (فقط ادمین)"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving users", e)
            return Response({'error': 'خطا در دریافت کاربران'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating user", e)
            return Response({'error': 'خطا در ایجاد کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(APIView):
    """API برای مشاهده، ویرایش و حذف کاربر خاص"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # فقط خود کاربر یا ادمین می‌تواند جزئیات را ببیند
            if request.user != user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving user", e)
            return Response({'error': 'خطا در دریافت کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # فقط خود کاربر یا ادمین می‌تواند ویرایش کند
            if request.user != user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating user", e)
            return Response({'error': 'خطا در به‌روزرسانی کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, user_id):
        try:
            # فقط ادمین می‌تواند کاربر را حذف کند
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting user", e)
            return Response({'error': 'خطا در حذف کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SetRoleView(APIView):
    """API برای تغییر نقش فعلی کاربر"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            role_name = request.data.get('role_name')
            if not role_name:
                return Response({'error': 'نام نقش الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
            if request.user.set_current_role(role_name):
                return Response({'message': f'نقش به {role_name} تغییر کرد'})
            return Response({'error': 'نقش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error setting role", e)
            return Response({'error': 'خطا در تغییر نقش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleListCreateView(APIView):
    """API برای مشاهده و ایجاد نقش‌ها (فقط ادمین)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            roles = Role.objects.all()
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving roles", e)
            return Response({'error': 'خطا در دریافت نقش‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating role", e)
            return Response({'error': 'خطا در ایجاد نقش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
