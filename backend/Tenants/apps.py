from django.apps import AppConfig

class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tenants'
    verbose_name = "Tenants Application"

    def ready(self) -> None: return super().ready()


