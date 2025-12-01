from .utils import get_current_tenant_db

class TenantRouter:
    """
    Router для направления запросов к правильной БД тенанта
    """
    def db_for_read(self, model, **hints):
        return get_current_tenant_db() or 'default'

    def db_for_write(self, model, **hints):
        return get_current_tenant_db() or 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Разрешаем отношения только между объектами одной БД
        db1 = getattr(obj1, '_state', None) and obj1._state.db or 'default'
        db2 = getattr(obj2, '_state', None) and obj2._state.db or 'default'
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Разрешаем миграции для всех БД
        return True