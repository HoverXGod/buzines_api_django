from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Content'
    verbose_name = 'Менеджер Контента'
    ordering = ['BaseSecurity', 'User']

    def ready(self) -> None: return None

