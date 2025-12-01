from django.apps import AppConfig


class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Payment'
    verbose_name = "Менеджер Платежей"
    ordering = ['BaseSecurity', 'Product']

    def ready(self) -> None: return None

