from django.http import HttpResponse
from openpyxl import Workbook
from import_export import resources
from import_export.admin import ExportMixin
import datetime
from django.db import models

class BusinessAdminMixin(ExportMixin):
    """Общие настройки для всех админ-классов"""
    list_per_page = 30
    export_formats = ['xlsx']
    list_select_related = True
    
    def get_export_resource_class(self):
        """Автоматическое создание ресурса для экспорта"""
        class DynamicResource(resources.ModelResource):
            class Meta:
                model = self.model
                exclude = ('password', 'base_password')
                export_order = [f.name for f in self.model._meta.fields if f.name not in ['password', 'base_password']]
                
        return DynamicResource

    def get_list_display(self, request):
        """Автоматическое форматирование полей"""
        base_fields = [f.name for f in self.model._meta.fields if f.name not in ['id', 'password']]
        return [self.format_field(field) for field in base_fields]

    def format_field(self, field_name):
        """Форматирование заголовков"""
        def formatter(obj):
            value = getattr(obj, field_name)
            if hasattr(value, 'pk'):
                return str(value)
            return value
        formatter.short_description = self.model._meta.get_field(field_name).verbose_name.title()
        return formatter

class UniversalExcelExportMixin:
    """Миксин для экспорта любой модели в Excel"""
    
    exclude_export_fields = ['id', 'password', 'base_password', 'secret_key']
    export_date_format = "%d.%m.%Y %H:%M"

    def get_export_filename(self, model_name):
        return f"{model_name}_export_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"

    def get_field_value(self, obj, field):
        value = getattr(obj, field.name)
        
        if isinstance(field, models.ForeignKey):
            return str(value) if value else ""
            
        if isinstance(value, datetime.datetime):
            return value.strftime(self.export_date_format)
            
        if isinstance(value, models.Model):
            return str(value)
            
        return value

    def export_to_excel(self, request, queryset):
        meta = self.model._meta
        fields = [
            field for field in meta.fields 
            if field.name not in self.exclude_export_fields
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = meta.verbose_name_plural[:30]

        # Заголовки
        headers = [field.verbose_name for field in fields]
        ws.append(headers)

        # Данные
        for obj in queryset.select_related():
            row = []
            for field in fields:
                try:
                    value = self.get_field_value(obj, field)
                    row.append(value)
                except Exception as e:
                    row.append(f"Error: {str(e)}")
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{self.get_export_filename(meta.model_name)}"'},
        )
        wb.save(response)
        return response
    
    export_to_excel.short_description = "📤 Экспорт выбранных записей в Excel"