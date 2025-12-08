from business_api.celery import app

@app.task(bind=True)
def _create_database_task(self, db_name: type[str]):
    from .utils import _add_database_to_settings, _migrate_database, load_tenants_config
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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

    cursor.execute(f'CREATE DATABASE "{db_name}"')

    # Добавляем БД в настройки Django
    _add_database_to_settings(db_name, base_config)

    # Запускаем миграции в фоне
    _migrate_database(db_name)

    cursor.close()
    conn.close()
