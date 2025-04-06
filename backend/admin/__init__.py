from django.contrib import admin
from .mixins import BusinessAdminMixin, UniversalExcelExportMixin

# Подключение к базовому классу админки
class BaseAdmin(admin.ModelAdmin, UniversalExcelExportMixin):
    actions = ['export_to_excel']
    list_per_page = 30

    # Для оптимизации запросов при экспорте
    def get_export_queryset(self, request):
        return super().get_queryset(request).select_related()

# Настройки глобальной админки
admin.site.site_header = "Панель управления магазином"
admin.site.site_title = "Магазин :: Администрирование"
admin.site.index_title = "Главная панель"
admin.site.empty_value_display = "—"