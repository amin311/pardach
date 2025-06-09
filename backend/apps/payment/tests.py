import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal
from unittest.mock import patch, Mock
from .models import Payment, Transaction
from apps.orders.models import Order
from apps.business.models import Business

User = get_user_model()

@pytest.mark.django_db
class PaymentTestCase(TestCase):
    """تست‌های سیستم پرداخت"""
    
    def setUp(self):
        """تنظیمات اولیه برای تست‌ها"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.business = Business.objects.create(
            name='تست بیزنس',
            owner=self.user
        )
        
        self.order = Order.objects.create(
            customer=self.user,
            business=self.business,
            total_price=Decimal('100000'),
            status='pending'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_payment(self):
        """تست ایجاد پرداخت"""
        payment_data = {
            'order': self.order.id,
            'amount': '50000',
            'payment_method': 'zarinpal'
        }
        
        response = self.client.post('/api/payment/payments/', payment_data)
        self.assertEqual(response.status_code, 201)
        
        payment = Payment.objects.get(id=response.data['id'])
        self.assertEqual(payment.amount, Decimal('50000'))
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_request_creation(self):
        """تست ایجاد درخواست پرداخت"""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('50000'),
            payment_method='zarinpal'
        )
        
        with patch('apps.payment.models.Payment.create_payment_request') as mock_request:
            mock_request.return_value = {
                'status': 'success',
                'authority': 'test_authority_123',
                'url': 'https://sandbox.zarinpal.com/pg/StartPay/test_authority_123'
            }
            
            result = payment.create_payment_request()
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('authority', result)
            self.assertIn('url', result)
    
    def test_payment_verification(self):
        """تست تأیید پرداخت"""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('50000'),
            payment_method='zarinpal',
            authority='test_authority_123',
            status='pending'
        )
        
        with patch('apps.payment.models.Payment.verify_payment') as mock_verify:
            mock_verify.return_value = {
                'status': 'success',
                'ref_id': 'test_ref_123'
            }
            
            result = payment.verify_payment('test_authority_123')
            
            self.assertEqual(result['status'], 'success')
            payment.refresh_from_db()
            self.assertEqual(payment.status, 'completed')
    
    def test_transaction_creation(self):
        """تست ایجاد تراکنش"""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('50000'),
            payment_method='zarinpal'
        )
        
        transaction = Transaction.objects.create(
            payment=payment,
            amount=Decimal('50000'),
            transaction_type='payment',
            status='pending'
        )
        
        self.assertEqual(transaction.payment, payment)
        self.assertEqual(transaction.amount, Decimal('50000'))
        self.assertEqual(transaction.status, 'pending')
    
    def test_payment_flow_complete(self):
        """تست کامل فرآیند پرداخت"""
        # مرحله 1: ایجاد پرداخت
        payment_data = {
            'order': self.order.id,
            'amount': '50000',
            'payment_method': 'zarinpal'
        }
        
        response = self.client.post('/api/payment/payments/', payment_data)
        payment_id = response.data['id']
        
        # مرحله 2: درخواست پرداخت
        with patch('apps.payment.models.Payment.create_payment_request') as mock_request:
            mock_request.return_value = {
                'status': 'success',
                'authority': 'test_authority_123',
                'url': 'https://sandbox.zarinpal.com/pg/StartPay/test_authority_123'
            }
            
            response = self.client.post(f'/api/payment/payments/{payment_id}/request/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('url', response.data)
        
        # مرحله 3: تأیید پرداخت
        with patch('apps.payment.models.Payment.verify_payment') as mock_verify:
            mock_verify.return_value = {
                'status': 'success',
                'ref_id': 'test_ref_123'
            }
            
            verify_data = {
                'authority': 'test_authority_123',
                'status': 'OK'
            }
            
            response = self.client.post('/api/payment/verify/', verify_data)
            self.assertEqual(response.status_code, 200)
            
            # بررسی تغییر وضعیت پرداخت
            payment = Payment.objects.get(id=payment_id)
            self.assertEqual(payment.status, 'completed')
    
    def test_payment_failure(self):
        """تست شکست پرداخت"""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('50000'),
            payment_method='zarinpal',
            authority='test_authority_123',
            status='pending'
        )
        
        with patch('apps.payment.models.Payment.verify_payment') as mock_verify:
            mock_verify.return_value = {
                'status': 'failed',
                'error': 'Payment failed'
            }
            
            result = payment.verify_payment('test_authority_123')
            
            self.assertEqual(result['status'], 'failed')
            payment.refresh_from_db()
            self.assertEqual(payment.status, 'failed')
    
    def test_payment_api_permissions(self):
        """تست مجوزهای API پرداخت"""
        # تست بدون احراز هویت
        anonymous_client = APIClient()
        
        payment_data = {
            'order': self.order.id,
            'amount': '50000',
            'payment_method': 'zarinpal'
        }
        
        response = anonymous_client.post('/api/payment/payments/', payment_data)
        self.assertEqual(response.status_code, 401)
        
        # تست با کاربر دیگر
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        
        response = other_client.post('/api/payment/payments/', payment_data)
        # باید خطای مجوز یا عدم دسترسی به سفارش دریافت کند
        self.assertIn(response.status_code, [403, 404])
