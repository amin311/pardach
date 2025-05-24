from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SetDesignConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.set_design'
    verbose_name = _('ست‌بندی')
    
    def ready(self):
        import apps.set_design.signals  # noqa 