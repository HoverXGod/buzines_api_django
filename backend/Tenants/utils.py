import os
import yaml
import threading
from pathlib import Path
from django.conf import settings
from django.db import connections
import subprocess
from core.cache import cache_method
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .tasks import _create_database_task
from django.core.cache import cache

# Thread-local storage для хранения текущей БД тенанта
_thread_local = threading.local()


def get_current_tenant_db():
    """Получает текущую базу данных тенанта"""
    return getattr(_thread_local, 'tenant_db', None)


def set_current_tenant_db(db_name):
    """Устанавливает текущую базу данных тенанта"""
    _thread_local.tenant_db = db_name

def clear_tenant_db():
    """Очищает текущую базу данных тенанта"""
    if hasattr(_thread_local, 'tenant_db'):
        del _thread_local.tenant_db

@cache_method([],timeout=18*60*60)
def load_tenants_config():
    """Загружает конфигурацию из tenants.yaml"""
    config_path = Path(__file__).resolve().parent.parent / 'tenants.yaml'

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_tenant_db_name(domain):
    """Преобразует домен в имя базы данных"""
    return domain.replace('.', '_') + '_cloude'

def db_exists(db_name: type[str]) -> bool:
    base_config = load_tenants_config()['databases']['tenant_template'].copy()
    conn: any = psycopg2.connect(
        dbname='postgres',
        user=base_config.get('USER', 'root'),
        password=base_config.get('PASSWORD', 'root'),
        host=base_config.get('HOST', 'localhost'),
        port=base_config.get('PORT', 5432)
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor: any = conn.cursor()

    # Проверяем существование базы
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = True if cursor.fetchone() else False

    cursor.close()
    conn.close()

    if exists:
        cache.set(db_name, "exists", timeout=18*60*60)
        _add_database_to_settings(db_name, base_config)

    return exists

def create_database_if_not_exists(db_name):
    """Создает базу данных если она не существует"""
    # Для PostgreSQL

    base_config = load_tenants_config()['databases']['tenant_template'].copy()

    try:
        _create_database_task.delay(db_name)
        _add_database_to_settings(db_name, base_config)
        cache.set(db_name, "exists", timeout=18 * 60 * 60)

    except Exception as e:
        print(f"Error creating database {db_name}: {e}")

def _add_database_to_settings(db_name, base_config):
    """Добавляет базу данных в настройки Django"""
    from django.conf import settings

    db_config = base_config.copy()
    db_config['NAME'] = db_name
    # Добавляем БД в DATABASES если её там нет
    if db_name not in settings.DATABASES:
        settings.DATABASES[db_name] = db_config


def _migrate_database(db_name):
    """Применяет миграции для базы данных"""
    from django.core.management import call_command

    try:
        print(f"Starting migrations for database: {db_name}")

        # Используем manage.py для миграций
        call_command("migrate", database=db_name)

        if result.returncode == 0:
            print(f"Successfully migrated database: {db_name}")
        else:
            print(f"Migration failed for {db_name}: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"Migration timeout for {db_name}")
    except Exception as e:
        print(f"Error migrating database {db_name}: {e}")


@cache_method([],timeout=20*60)
def get_tenant_databases():
    """Возвращает все базы данных тенантов"""
    config = load_tenants_config()
    databases = {'default': config['databases']['default']}
    return databases