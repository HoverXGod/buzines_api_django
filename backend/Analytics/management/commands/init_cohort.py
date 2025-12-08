from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize performance records for all active products'

    def add_arguments(self, parser):
        parser.add_arguemnt('db_name', type=str, help='')

    def handle(self, *args, **options):
        try:
            apps.get_model('Analytics', 'CohortAnalysis').objects.add_entry(options['db_name'])
        except OperationalError:
                logger.error("Database not ready, skipping initialization")