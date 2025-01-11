from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'User'
    verbose_name = 'User Application'
    ordering = ['Encryption', 'BaseSecurity']

    def ready(self) -> None:
        return super().ready()
