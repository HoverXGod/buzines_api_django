from django.core.management import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Clear all caches'

    def handle(self, *args, **options):
        cache.clear()
        cache._cache.clear()