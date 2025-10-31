from django.apps import AppConfig


class CacheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Cache'
    verbose_name = "Управление кешами"
