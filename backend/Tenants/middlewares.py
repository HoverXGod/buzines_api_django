from .utils import get_tenant_db_name, create_database_if_not_exists, load_tenants_config, set_current_tenant_db, \
    clear_tenant_db


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем домен из заголовка
        domain = request.META.get('HTTP_X_DOMAIN')

        if domain:
            db_name = get_tenant_db_name(domain)
            set_current_tenant_db(db_name)

            # Проверяем и создаем БД если нужно
            config = load_tenants_config()
            create_database_if_not_exists(db_name, config['databases'])

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