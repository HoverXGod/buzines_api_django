from django.apps import AppConfig

class ApiKeysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Api_Keys'
    verbose_name = "API_KEYS Application"
    ordering = ['Encryption', 'BaseSecurity', 'User']

    def ready(self) -> None:
        return super().ready()

