from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CRM'
    verbose_name = 'CRM Application'
    ordering = ['BaseSecurity', 'Content']

    def ready(self) -> None: return None

