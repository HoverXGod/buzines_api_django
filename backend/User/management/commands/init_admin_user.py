from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        try:
            user_model = get_user_model()

            try:
                admin_user = user_model.objects.get(username="admin")
                admin_user.password = "admin"
                admin_user.super_user = True
            except:
                admin_user = User.register_user("admin", "admin", "admin")
                admin_user.super_user = True
        except:
                pass