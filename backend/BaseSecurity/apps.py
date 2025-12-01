from django.apps import AppConfig 


class BaseSecurityConfigrest_framework(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BaseSecurity'
    verbose_name = "Приложение Безопасности"
    ordering = ['Encryption', 'Api_Keys', 'rest_framework', 'User']

    def ready(self) -> None: return None


