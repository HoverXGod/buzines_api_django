from django.apps import AppConfig
from django.core.signals import request_started
from django.dispatch import receiver

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'User'
    verbose_name = 'Менеджер Пользователей'
    ordering = ['Encryption', 'BaseSecurity']

    def ready(self) -> None:
        @receiver(request_started)
        def init_admin_user_receiver(sender, **kwargs):
            from django.core.management import call_command

            call_command('init_admin_user')
            request_started.disconnect(init_admin_user_receiver)

        return super().ready()
