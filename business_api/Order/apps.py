from django.apps import AppConfig


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Order'
    verbose_name = 'Order Application'
    ordering = ['BaseSecurity', 'Product']
