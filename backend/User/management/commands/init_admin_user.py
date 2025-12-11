from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        try:
            user_model = apps.get_model("User.User")

            try:
                admin_user = user_model.objects.get(username="admin")
                admin_user.password = "123"
                admin_user.super_user = True
            except:
                admin_user = user_model.register_user("admin", "123", "admin")
                admin_user.super_user = True

        except Exception as e: print(e)