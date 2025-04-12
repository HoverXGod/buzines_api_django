from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import OperationalError
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize performance records for all active products'

    def handle(self, *args, **options):
        try:
            Product = apps.get_model('Product', 'Product')
            ProductPerformance = apps.get_model('Analytics', 'ProductPerformance')
            
            active_products = Product.objects.filter()
            
            for product in active_products:
                try: ProductPerformance.objects.get(
                    product=product,
                )
                except ObjectDoesNotExist:
                    ProductPerformance.objects.add_entry(product)
                    logger.info(f"Created performance record for {product.name}")
        except OperationalError:
            logger.error("Database not ready, skipping initialization")