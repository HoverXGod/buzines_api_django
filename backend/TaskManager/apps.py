from django.apps import AppConfig


class TaskmanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TaskManager'
    verbose_name = 'Менеджер Тасков'

    def ready(self) -> None: return None

