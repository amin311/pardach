from django.apps import AppConfig  
  
  
class NotificationConfig(AppConfig):  
    default_auto_field = 'django.db.models.BigAutoField'  
    name = 'apps.notification' 

    def ready(self):
        """Connect signal handlers for the notification app."""
        from . import signals  # noqa
