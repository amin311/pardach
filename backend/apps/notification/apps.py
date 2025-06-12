from django.apps import AppConfig  
  
  
<<<<<<< HEAD
class NotificationConfig(AppConfig):  
    default_auto_field = 'django.db.models.BigAutoField'  
    name = 'apps.notification' 

    def ready(self):
        """Connect signal handlers for the notification app."""
=======
class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notification'

    def ready(self):
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
        from . import signals  # noqa
