from django.core.management.base import BaseCommand
from django.db import connections
import psycopg2
from Tenants.utils import get_tenant_db_name, load_tenants_config


class Command(BaseCommand):
    help = 'Initialize tenant database'

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help='Tenant domain')

    def handle(self, *args, **options):
        domain = options['domain']
        db_name = get_tenant_db_name(domain)
        config = load_tenants_config()

        self.stdout.write(f"Initializing tenant database for {domain}...")

        # Создаем БД если не существует
        from Tenants.settings import create_database_if_not_exists
        create_database_if_not_exists(db_name, config['databases'])

        self.stdout.write(
            self.style.SUCCESS(f"Tenant database {db_name} initialized successfully")
        )