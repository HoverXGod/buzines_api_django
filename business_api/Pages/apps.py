from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Pages'
    verbose_name = 'Pages Application'
    ordering = ['BaseSecurity', 'Content']
