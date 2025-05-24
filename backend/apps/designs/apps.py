from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DesignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.designs'
    verbose_name = _('طراحی‌ها')

    def ready(self):
        """اجرای کدهای لازم هنگام بارگذاری اپلیکیشن"""
        # بارگذاری signals در صورت نیاز
        pass
