from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main'
    verbose_name = _('صفحه اصلی')

    def ready(self):
        """اجرای کدهای لازم هنگام بارگذاری اپلیکیشن"""
        # در صورت نیاز به سیگنال‌ها یا تنظیمات اولیه
        pass
