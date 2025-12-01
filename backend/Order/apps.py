from django.apps import AppConfig
from django.dispatch import receiver
from django.core.signals import request_started
from django.db.utils import ProgrammingError

class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Order'
    verbose_name = 'Менеджер Заказов'
    ordering = ['BaseSecurity', 'Product', 'Payment']

    def ready(self) -> None:
        @receiver(request_started)
        def init_base_salse_channel(sender, **kwargs):
            from django.core.management import call_command

            try: call_command('init_base_channel')
            except ProgrammingError: pass
            request_started.disconnect(init_base_salse_channel)