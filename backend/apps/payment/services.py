import requests
import logging
from django.conf import settings
from .models import Payment, Transaction

logger = logging.getLogger(__name__)

class PaymentService:
    """کلاس پایه برای سرویس‌های پرداخت"""
    
    def __init__(self, payment):
        self.payment = payment
    
    def request_payment(self):
        """درخواست پرداخت به درگاه - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError("این متد باید در کلاس فرزند پیاده‌سازی شود")
    
    def verify_payment(self, data):
        """تایید پرداخت از درگاه - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError("این متد باید در کلاس فرزند پیاده‌سازی شود")
    
    @staticmethod
    def create_transaction(payment, amount, status='pending', authority=None, ref_id=None, gateway_response=None):
        """ایجاد تراکنش جدید برای پرداخت"""
        return Transaction.objects.create(
            payment=payment,
            amount=amount,
            status=status,
            authority=authority,
            ref_id=ref_id,
            gateway_response=gateway_response
        )
    
    @staticmethod
    def update_payment_status(payment, status, payment_data=None):
        """بروزرسانی وضعیت پرداخت"""
        payment.status = status
        if payment_data:
            payment.payment_data = payment_data
        payment.save()
        
        # اگر پرداخت موفق بود، وضعیت سفارش را به processing تغییر می‌دهیم
        if status == 'successful':
            order = payment.order
            order.status = 'processing'
            order.save()


class ZarinPalService(PaymentService):
    """سرویس پرداخت زرین‌پال"""
    
    # آدرس‌های API زرین‌پال
    ZARINPAL_PAYMENT_URL = 'https://api.zarinpal.com/pg/v4/payment/request.json'
    ZARINPAL_VERIFY_URL = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
    ZARINPAL_GATEWAY_URL = 'https://www.zarinpal.com/pg/StartPay/{authority}'
    
    # در محیط آزمایشی از آدرس‌های تست استفاده می‌کنیم
    ZARINPAL_SANDBOX_PAYMENT_URL = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
    ZARINPAL_SANDBOX_VERIFY_URL = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
    ZARINPAL_SANDBOX_GATEWAY_URL = 'https://sandbox.zarinpal.com/pg/StartPay/{authority}'
    
    def __init__(self, payment):
        super().__init__(payment)
        # آیا در محیط آزمایشی هستیم؟
        self.is_sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        # مرچنت کد زرین‌پال
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')
    
    def get_payment_url(self):
        """آدرس درخواست پرداخت"""
        return self.ZARINPAL_SANDBOX_PAYMENT_URL if self.is_sandbox else self.ZARINPAL_PAYMENT_URL
    
    def get_verify_url(self):
        """آدرس تایید پرداخت"""
        return self.ZARINPAL_SANDBOX_VERIFY_URL if self.is_sandbox else self.ZARINPAL_VERIFY_URL
    
    def get_gateway_url(self, authority):
        """آدرس درگاه پرداخت با کد پیگیری"""
        base_url = self.ZARINPAL_SANDBOX_GATEWAY_URL if self.is_sandbox else self.ZARINPAL_GATEWAY_URL
        return base_url.format(authority=authority)
    
    def request_payment(self):
        """درخواست پرداخت به درگاه زرین‌پال"""
        try:
            # آماده‌سازی داده‌های درخواست
            data = {
                "merchant_id": self.merchant_id,
                "amount": int(self.payment.amount),
                "callback_url": self.payment.callback_url,
                "description": self.payment.description or f"پرداخت سفارش {self.payment.order.id}",
                "metadata": {
                    "email": self.payment.user.email,
                    "mobile": getattr(self.payment.user, 'phone_number', ''),
                    "order_id": str(self.payment.order.id)
                }
            }
            
            # ارسال درخواست به زرین‌پال
            response = requests.post(self.get_payment_url(), json=data)
            result = response.json()
            
            # ثبت تراکنش جدید
            self.create_transaction(
                payment=self.payment,
                amount=self.payment.amount,
                gateway_response=result
            )
            
            # بررسی پاسخ زرین‌پال
            if result.get('data', {}).get('code') == 100:
                authority = result['data']['authority']
                # بروزرسانی داده‌های پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'authority': authority,
                    'gateway_response': result,
                })
                self.update_payment_status(self.payment, 'pending', payment_data)
                
                # ایجاد تراکنش با کد پیگیری
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='pending',
                    authority=authority,
                    gateway_response=result
                )
                
                # آدرس هدایت به درگاه پرداخت
                return {
                    'success': True,
                    'url': self.get_gateway_url(authority),
                    'authority': authority
                }
            else:
                # خطا در درخواست پرداخت
                error_code = result.get('errors', {}).get('code')
                error_message = result.get('errors', {}).get('message', 'خطا در درخواست پرداخت')
                logger.error(f"ZarinPal payment request error: {error_code} - {error_message}")
                
                # بروزرسانی وضعیت پرداخت
                self.update_payment_status(self.payment, 'failed', {
                    'error_code': error_code,
                    'error_message': error_message,
                    'gateway_response': result
                })
                return {
                    'success': False,
                    'message': error_message
                }
        except Exception as e:
            logger.error(f"ZarinPal payment request exception: {str(e)}")
            self.update_payment_status(self.payment, 'failed', {
                'error_message': str(e)
            })
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }
    
    def verify_payment(self, authority, status="OK"):
        """تایید پرداخت از درگاه زرین‌پال"""
        try:
            # اگر وضعیت درگاه OK نباشد، پرداخت ناموفق بوده است
            if status != "OK":
                self.update_payment_status(self.payment, 'failed', {
                    'authority': authority,
                    'error_message': 'پرداخت توسط کاربر لغو شد'
                })
                return {
                    'success': False,
                    'message': 'پرداخت توسط کاربر لغو شد'
                }
            
            # آماده‌سازی داده‌های تایید
            data = {
                "merchant_id": self.merchant_id,
                "amount": int(self.payment.amount),
                "authority": authority
            }
            
            # ارسال درخواست تایید به زرین‌پال
            response = requests.post(self.get_verify_url(), json=data)
            result = response.json()
            
            # بررسی پاسخ تایید
            if result.get('data', {}).get('code') == 100:
                # پرداخت موفق
                ref_id = result['data']['ref_id']
                
                # بروزرسانی داده‌های پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'authority': authority,
                    'ref_id': ref_id,
                    'verify_response': result
                })
                self.update_payment_status(self.payment, 'successful', payment_data)
                
                # ایجاد تراکنش موفق
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='successful',
                    authority=authority,
                    ref_id=ref_id,
                    gateway_response=result
                )
                
                return {
                    'success': True,
                    'ref_id': ref_id,
                    'message': 'پرداخت با موفقیت انجام شد'
                }
            else:
                # خطا در تایید پرداخت
                error_code = result.get('errors', {}).get('code')
                error_message = result.get('errors', {}).get('message', 'خطا در تایید پرداخت')
                logger.error(f"ZarinPal payment verification error: {error_code} - {error_message}")
                
                # بروزرسانی وضعیت پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'authority': authority,
                    'error_code': error_code,
                    'error_message': error_message,
                    'verify_response': result
                })
                self.update_payment_status(self.payment, 'failed', payment_data)
                
                # ایجاد تراکنش ناموفق
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='failed',
                    authority=authority,
                    gateway_response=result
                )
                
                return {
                    'success': False,
                    'message': error_message
                }
        except Exception as e:
            logger.error(f"ZarinPal payment verification exception: {str(e)}")
            
            # بروزرسانی وضعیت پرداخت
            payment_data = self.payment.payment_data or {}
            payment_data.update({
                'authority': authority,
                'error_message': str(e)
            })
            self.update_payment_status(self.payment, 'failed', payment_data)
            
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }


class IdPayService(PaymentService):
    """سرویس پرداخت آی‌دی پی"""
    
    # آدرس‌های API آی‌دی پی
    IDPAY_PAYMENT_URL = 'https://api.idpay.ir/v1.1/payment'
    IDPAY_VERIFY_URL = 'https://api.idpay.ir/v1.1/payment/verify'
    
    def __init__(self, payment):
        super().__init__(payment)
        # API Key آی‌دی پی
        self.api_key = getattr(settings, 'IDPAY_API_KEY', 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')
        # آیا در محیط آزمایشی هستیم؟
        self.is_sandbox = getattr(settings, 'IDPAY_SANDBOX', True)
    
    def get_headers(self):
        """هدرهای مورد نیاز برای ارتباط با آی‌دی پی"""
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
        }
        if self.is_sandbox:
            headers['X-SANDBOX'] = '1'
        return headers
    
    def request_payment(self):
        """درخواست پرداخت به درگاه آی‌دی پی"""
        try:
            # آماده‌سازی داده‌های درخواست
            data = {
                "order_id": str(self.payment.transaction_id),
                "amount": int(self.payment.amount),
                "callback": self.payment.callback_url,
                "desc": self.payment.description or f"پرداخت سفارش {self.payment.order.id}",
                "name": self.payment.user.get_full_name() or self.payment.user.username,
                "mail": self.payment.user.email,
                "phone": getattr(self.payment.user, 'phone_number', '')
            }
            
            # ارسال درخواست به آی‌دی پی
            response = requests.post(self.IDPAY_PAYMENT_URL, json=data, headers=self.get_headers())
            result = response.json()
            
            # ثبت تراکنش جدید
            self.create_transaction(
                payment=self.payment,
                amount=self.payment.amount,
                gateway_response=result
            )
            
            # بررسی پاسخ آی‌دی پی
            if 'id' in result and 'link' in result:
                # بروزرسانی داده‌های پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'id_pay_id': result['id'],
                    'gateway_response': result,
                })
                self.update_payment_status(self.payment, 'pending', payment_data)
                
                # ایجاد تراکنش با کد پیگیری
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='pending',
                    authority=result['id'],
                    gateway_response=result
                )
                
                # آدرس هدایت به درگاه پرداخت
                return {
                    'success': True,
                    'url': result['link'],
                    'authority': result['id']
                }
            else:
                # خطا در درخواست پرداخت
                error_code = result.get('error_code')
                error_message = result.get('error_message', 'خطا در درخواست پرداخت')
                logger.error(f"IdPay payment request error: {error_code} - {error_message}")
                
                # بروزرسانی وضعیت پرداخت
                self.update_payment_status(self.payment, 'failed', {
                    'error_code': error_code,
                    'error_message': error_message,
                    'gateway_response': result
                })
                return {
                    'success': False,
                    'message': error_message
                }
        except Exception as e:
            logger.error(f"IdPay payment request exception: {str(e)}")
            self.update_payment_status(self.payment, 'failed', {
                'error_message': str(e)
            })
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }
    
    def verify_payment(self, id_pay_id, status):
        """تایید پرداخت از درگاه آی‌دی پی"""
        try:
            # بررسی وضعیت از آی‌دی پی
            if status != 10:
                # پرداخت ناموفق بوده است
                status_message = "پرداخت ناموفق بود"
                if status == 1:
                    status_message = "پرداخت انجام نشده است"
                elif status == 2:
                    status_message = "پرداخت ناموفق بوده است"
                elif status == 3:
                    status_message = "خطا رخ داده است"
                elif status == 4:
                    status_message = "بلوکه شده"
                elif status == 5:
                    status_message = "برگشت به پرداخت کننده"
                elif status == 6:
                    status_message = "برگشت خورده سیستمی"
                elif status == 7:
                    status_message = "انصراف از پرداخت"
                
                self.update_payment_status(self.payment, 'failed', {
                    'id_pay_id': id_pay_id,
                    'error_message': status_message
                })
                return {
                    'success': False,
                    'message': status_message
                }
            
            # آماده‌سازی داده‌های تایید
            data = {
                "id": id_pay_id,
                "order_id": str(self.payment.transaction_id)
            }
            
            # ارسال درخواست تایید به آی‌دی پی
            response = requests.post(self.IDPAY_VERIFY_URL, json=data, headers=self.get_headers())
            result = response.json()
            
            # بررسی پاسخ تایید
            if 'status' in result and result['status'] == 100:
                # پرداخت موفق
                ref_id = result.get('payment', {}).get('track_id')
                
                # بروزرسانی داده‌های پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'id_pay_id': id_pay_id,
                    'ref_id': ref_id,
                    'verify_response': result
                })
                self.update_payment_status(self.payment, 'successful', payment_data)
                
                # ایجاد تراکنش موفق
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='successful',
                    authority=id_pay_id,
                    ref_id=ref_id,
                    gateway_response=result
                )
                
                return {
                    'success': True,
                    'ref_id': ref_id,
                    'message': 'پرداخت با موفقیت انجام شد'
                }
            else:
                # خطا در تایید پرداخت
                error_code = result.get('error_code')
                error_message = result.get('error_message', 'خطا در تایید پرداخت')
                logger.error(f"IdPay payment verification error: {error_code} - {error_message}")
                
                # بروزرسانی وضعیت پرداخت
                payment_data = self.payment.payment_data or {}
                payment_data.update({
                    'id_pay_id': id_pay_id,
                    'error_code': error_code,
                    'error_message': error_message,
                    'verify_response': result
                })
                self.update_payment_status(self.payment, 'failed', payment_data)
                
                # ایجاد تراکنش ناموفق
                self.create_transaction(
                    payment=self.payment,
                    amount=self.payment.amount,
                    status='failed',
                    authority=id_pay_id,
                    gateway_response=result
                )
                
                return {
                    'success': False,
                    'message': error_message
                }
        except Exception as e:
            logger.error(f"IdPay payment verification exception: {str(e)}")
            
            # بروزرسانی وضعیت پرداخت
            payment_data = self.payment.payment_data or {}
            payment_data.update({
                'id_pay_id': id_pay_id,
                'error_message': str(e)
            })
            self.update_payment_status(self.payment, 'failed', payment_data)
            
            return {
                'success': False,
                'message': 'خطا در ارتباط با درگاه پرداخت'
            }


class InternalPaymentService(PaymentService):
    """سرویس پرداخت داخلی (شبیه‌سازی‌شده)"""
    
    def request_payment(self):
        """شبیه‌سازی درخواست پرداخت"""
        try:
            # ایجاد یک شناسه پرداخت داخلی
            authority = f"INT-{self.payment.transaction_id}"
            
            # بروزرسانی داده‌های پرداخت
            payment_data = self.payment.payment_data or {}
            payment_data.update({
                'authority': authority,
                'simulation': True
            })
            self.update_payment_status(self.payment, 'pending', payment_data)
            
            # ایجاد تراکنش با کد پیگیری
            self.create_transaction(
                payment=self.payment,
                amount=self.payment.amount,
                status='pending',
                authority=authority
            )
            
            # URL شبیه‌سازی پرداخت
            callback_url = self.payment.callback_url
            if '?' in callback_url:
                simulated_url = f"{callback_url}&Authority={authority}&Status=OK"
            else:
                simulated_url = f"{callback_url}?Authority={authority}&Status=OK"
            
            return {
                'success': True,
                'url': simulated_url,
                'authority': authority,
                'simulation': True,
                'message': 'پرداخت در حالت شبیه‌سازی است. برای تایید روی لینک کلیک کنید.'
            }
        except Exception as e:
            logger.error(f"Internal payment request exception: {str(e)}")
            self.update_payment_status(self.payment, 'failed', {
                'error_message': str(e)
            })
            return {
                'success': False,
                'message': 'خطا در شبیه‌سازی پرداخت'
            }
    
    def verify_payment(self, authority, status="OK"):
        """شبیه‌سازی تایید پرداخت"""
        try:
            if status != "OK":
                self.update_payment_status(self.payment, 'failed', {
                    'authority': authority,
                    'error_message': 'پرداخت توسط کاربر لغو شد'
                })
                return {
                    'success': False,
                    'message': 'پرداخت توسط کاربر لغو شد'
                }
            
            # شبیه‌سازی پرداخت موفق
            ref_id = f"REF-{self.payment.transaction_id}"
            
            # بروزرسانی داده‌های پرداخت
            payment_data = self.payment.payment_data or {}
            payment_data.update({
                'authority': authority,
                'ref_id': ref_id,
                'simulation': True
            })
            self.update_payment_status(self.payment, 'successful', payment_data)
            
            # ایجاد تراکنش موفق
            self.create_transaction(
                payment=self.payment,
                amount=self.payment.amount,
                status='successful',
                authority=authority,
                ref_id=ref_id
            )
            
            return {
                'success': True,
                'ref_id': ref_id,
                'message': 'پرداخت با موفقیت شبیه‌سازی شد'
            }
        except Exception as e:
            logger.error(f"Internal payment verification exception: {str(e)}")
            
            # بروزرسانی وضعیت پرداخت
            payment_data = self.payment.payment_data or {}
            payment_data.update({
                'authority': authority,
                'error_message': str(e)
            })
            self.update_payment_status(self.payment, 'failed', payment_data)
            
            return {
                'success': False,
                'message': 'خطا در شبیه‌سازی تایید پرداخت'
            }


def get_payment_service(payment):
    """بر اساس نوع درگاه، سرویس پرداخت مناسب را برمی‌گرداند"""
    if payment.gateway == 'zarinpal':
        return ZarinPalService(payment)
    elif payment.gateway == 'idpay':
        return IdPayService(payment)
    else:
        return InternalPaymentService(payment) 