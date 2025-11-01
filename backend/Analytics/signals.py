# apps/analytics/disability.py
from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command

@receiver(post_migrate)
def create_initial_records(sender, **kwargs):
    print(sender.name)
    if sender.name == 'Analytics':
        call_command('init_performance')