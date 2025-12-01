from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Product'
    verbose_name = 'Менеджер Товаров'
    ordering = ['BaseSecurity']

    def ready(self) -> None: return None

