from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = _('سفارش‌ها')
    
    def ready(self):
        """
        متد برای اجرای کدهای لازم در زمان بارگذاری اپلیکیشن
        """
        # import signals if needed
        # from . import signals
        pass
