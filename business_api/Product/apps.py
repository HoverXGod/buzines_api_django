from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Product'
    verbose_name = 'Product Application'
    ordering = ['BaseSecurity']
