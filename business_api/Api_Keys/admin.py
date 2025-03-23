from django.contrib import admin
from .models import Api_key
from admin import BaseAdmin
from django.utils.html import format_html


@admin.register(Api_key)
class ApiKeyAdmin(BaseAdmin):
    list_display = ('key_name', 'user_badge', 'status_badge', 'dates')
    search_fields = ('key_name', 'user__username')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('🔑 Основное', {
            'fields': ('key_name', 'user', 'is_active'),
            'description': 'Основные параметры API-ключа'
        }),
        ('📅 Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('ℹ️ Дополнительно', {
            'fields': ('help_text',),
            'classes': ('collapse',)
        }),
    )

    def user_badge(self, obj):
        return format_html(
            "{}<br>📞 {}",
            obj.user.username,
            obj.user.phone_number
        )
    user_badge.short_description = "Пользователь"

    def status_badge(self, obj):
        color = '#4CAF50' if obj.is_active else '#F44336'
        return format_html(
            '<span style="color: {};">●</span> {}',
            color,
            "Активен" if obj.is_active else "Неактивен"
        )
    status_badge.short_description = "Статус"

    def dates(self, obj):
        return format_html(
            "Создан: {}<br>Обновлен: {}",
            obj.created_at.strftime("%d.%m.%Y"),
            obj.updated_at.strftime("%d.%m.%Y")
        )
    dates.short_description = "Даты"
