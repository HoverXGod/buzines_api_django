from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize performance records for all active products'

    def handle(self, *args, **options):
        try:
            apps.get_model('Analytics', 'CohortAnalysis').objects.add_entry()
            self.stdout.write(
                self.style.SUCCESS('Successfully initialized cohort records')
            )
        except OperationalError:
                logger.error("Database not ready, skipping initialization")