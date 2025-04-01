from django.apps import AppConfig
from django.core.management import call_command
from django.core.signals import request_started

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Analytics'
    verbose_name = "Аналитика"