from django.apps import AppConfig

def _admin_user_profile() -> None:
    from .models import User


    first_user = User.objects.get(username="admin")
    first_user.password = "admin"
    first_user.super_user = True
    # except:
    #     us = User.register_user("admin", "admin", "admin")
    #     us.super_user = True

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'User'
    verbose_name = 'Менеджер Пользователей'
    ordering = ['Encryption', 'BaseSecurity']

    def ready(self) -> None:
        _admin_user_profile()
        return super().ready()
