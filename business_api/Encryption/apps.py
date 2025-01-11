from django.apps import AppConfig
from .utils import Encryption

class EncryptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Encryption'
    verbose_name = "Encryption Application"

    def ready(self) -> None:
        pass
