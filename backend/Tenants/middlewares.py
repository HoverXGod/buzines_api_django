from .utils import get_tenant_db_name, create_database_if_not_exists, set_current_tenant_db, \
    clear_tenant_db, db_exists
from django.core.cache import cache

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем домен из заголовка
        domain = request.META.get('HTTP_X_DOMAIN')

        if domain:
            db_name = get_tenant_db_name(domain)

            if not cache.get(db_name):
                if db_exists(db_name):
                    set_current_tenant_db(db_name)
                else:
                    create_database_if_not_exists(db_name)
                    raise RuntimeError("Creating database")
            else:
                set_current_tenant_db(db_name)

            # Добавляем информацию в request для использования в views
            request.tenant_db = db_name
            request.tenant_domain = domain
        else:
            # Используем default базу данных
            set_current_tenant_db('default')
            request.tenant_db = 'default'
            request.tenant_domain = 'default'

        response = self.get_response(request)

        # Очищаем после обработки
        clear_tenant_db()

        return response

    def process_exception(self, request, exception):
        """Очищаем при исключениях"""
        clear_tenant_db()