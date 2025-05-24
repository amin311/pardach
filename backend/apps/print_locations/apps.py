from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PrintLocationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.print_locations'
    verbose_name = _('بخش‌های چاپ') 