from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.core.utils import log_error
from django.db.models import Q

# Create your views here.

class OrderListCreateView(APIView):
    """API برای لیست و ایجاد سفارش‌ها"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """دریافت لیست سفارش‌ها"""
        try:
            # اگر کاربر ادمین باشد همه سفارش‌ها را نمایش بده، در غیر اینصورت فقط سفارش‌های کاربر را نمایش بده
            if request.user.is_staff:
                orders = Order.objects.all()
            else:
                orders = Order.objects.filter(user=request.user)
                
            # فیلتر بر اساس وضعیت
            status_param = request.query_params.get('status')
            if status_param:
                orders = orders.filter(status=status_param)
                
            # جستجو
            query = request.query_params.get('q')
            if query:
                orders = orders.filter(
                    Q(notes__icontains=query) | 
                    Q(user__username__icontains=query) |
                    Q(user__email__icontains=query)
                )
                
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving orders", e)
            return Response({'error': 'خطا در دریافت سفارش‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """ایجاد سفارش جدید"""
        try:
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                order = serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating order", e)
            return Response({'error': 'خطا در ایجاد سفارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderDetailView(APIView):
    """API برای جزئیات، ویرایش و حذف سفارش"""
    permission_classes = [IsAuthenticated]

    def get_order(self, order_id, user):
        """دریافت سفارش با بررسی دسترسی"""
        try:
            order = Order.objects.get(id=order_id)
            if order.user != user and not user.is_staff:
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            return order, None
        except Order.DoesNotExist:
            return None, Response({'error': 'سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error(f"Error retrieving order {order_id}", e)
            return None, Response({'error': 'خطا در دریافت سفارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, order_id):
        """مشاهده جزئیات سفارش"""
        order, error_response = self.get_order(order_id, request.user)
        if error_response:
            return error_response
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, order_id):
        """ویرایش سفارش"""
        order, error_response = self.get_order(order_id, request.user)
        if error_response:
            return error_response
            
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        """حذف سفارش"""
        order, error_response = self.get_order(order_id, request.user)
        if error_response:
            return error_response
            
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderItemListCreateView(APIView):
    """API برای لیست و ایجاد آیتم‌های سفارش"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """دریافت آیتم‌های سفارش"""
        try:
            # بررسی دسترسی به سفارش
            try:
                order = Order.objects.get(id=order_id)
                if order.user != request.user and not request.user.is_staff:
                    return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            except Order.DoesNotExist:
                return Response({'error': 'سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
                
            items = OrderItem.objects.filter(order=order)
            serializer = OrderItemSerializer(items, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error(f"Error retrieving order items for order {order_id}", e)
            return Response({'error': 'خطا در دریافت آیتم‌های سفارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, order_id):
        """افزودن آیتم به سفارش"""
        try:
            # بررسی دسترسی به سفارش
            try:
                order = Order.objects.get(id=order_id)
                if order.user != request.user and not request.user.is_staff:
                    return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            except Order.DoesNotExist:
                return Response({'error': 'سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
                
            # اضافه کردن شناسه سفارش به داده‌های ارسالی
            data = request.data.copy()
            data['order'] = order_id
                
            serializer = OrderItemSerializer(data=data)
            if serializer.is_valid():
                item = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"Error creating order item for order {order_id}", e)
            return Response({'error': 'خطا در ایجاد آیتم سفارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderItemDetailView(APIView):
    """API برای جزئیات، ویرایش و حذف آیتم سفارش"""
    permission_classes = [IsAuthenticated]

    def get_order_item(self, item_id, user):
        """دریافت آیتم سفارش با بررسی دسترسی"""
        try:
            item = OrderItem.objects.get(id=item_id)
            if item.order.user != user and not user.is_staff:
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            return item, None
        except OrderItem.DoesNotExist:
            return None, Response({'error': 'آیتم سفارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error(f"Error retrieving order item {item_id}", e)
            return None, Response({'error': 'خطا در دریافت آیتم سفارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, item_id):
        """مشاهده جزئیات آیتم سفارش"""
        item, error_response = self.get_order_item(item_id, request.user)
        if error_response:
            return error_response
            
        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, item_id):
        """ویرایش آیتم سفارش"""
        item, error_response = self.get_order_item(item_id, request.user)
        if error_response:
            return error_response
            
        serializer = OrderItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        """حذف آیتم سفارش"""
        item, error_response = self.get_order_item(item_id, request.user)
        if error_response:
            return error_response
            
        order = item.order
        item.delete()
        # به‌روزرسانی قیمت کل سفارش
        order.calculate_total_price()
        return Response(status=status.HTTP_204_NO_CONTENT)
