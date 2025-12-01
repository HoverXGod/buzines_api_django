import os
import yaml
from pathlib import Path
from django.core.management import execute_from_command_line

BASE_DIR = Path(__file__).resolve().parent.parent

def load_tenants_config():
    with open(BASE_DIR / 'tenants.yaml', 'r') as file:
        return yaml.safe_load(file)

def get_tenant_db_name(domain):
    """Преобразует домен в имя базы данных"""
    return domain.replace('.', '_') + '_cloude'

def create_database_if_not_exists(db_name, tenant_config):
    """Создает базу данных если она не существует"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    # Конфиг для подключения к основной БД (без указания базы)
    base_config = tenant_config['tenant_template'].copy()

    try:
        # Подключаемся к postgres для создания БД
        conn = psycopg2.connect(
            dbname='postgres',
            user=base_config['USER'],
            password=base_config['PASSWORD'],
            host=base_config['HOST'],
            port=base_config['PORT']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверяем существование базы
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database: {db_name}")
            cursor.execute(f'CREATE DATABASE "{db_name}"')

            # Применяем миграции в фоне
            migrate_tenant_database(db_name, tenant_config)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database {db_name}: {e}")

def migrate_tenant_database(db_name, tenant_config):
    """Применяет миграции для базы данных тенанта"""
    import subprocess
    import threading

    def run_migrations():
        # Создаем временные настройки для миграций
        tenant_db_config = tenant_config['tenant_template'].copy()
        tenant_db_config['NAME'] = db_name

        # Запускаем миграции в отдельном процессе
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'your_project.settings'
        env['TENANT_DB_NAME'] = db_name

        try:
            # Используем subprocess для изоляции
            subprocess.run([
                'python', 'manage.py', 'migrate',
                '--database', db_name,
                '--no-input'
            ], env=env, check=True, capture_output=True)
            print(f"Migrations applied for {db_name}")
        except subprocess.CalledProcessError as e:
            print(f"Migration error for {db_name}: {e}")

    # Запускаем миграции в отдельном потоке
    thread = threading.Thread(target=run_migrations)
    thread.daemon = True
    thread.start()

def get_databases():
    """Динамически генерирует DATABASES настройку"""
    config = load_tenants_config()
    databases = {
        'default': config['databases']['default']
    }

    return databases

