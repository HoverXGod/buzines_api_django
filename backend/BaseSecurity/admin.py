from django.contrib import admin
from .models import AuditLog
from admin import BaseAdmin
from django.utils.html import format_html
import json

@admin.register(AuditLog)
class AuditLogAdmin(BaseAdmin):
    list_display = ('action', 'user_info', 'status_badge', 'timestamp')
    search_fields = ('action', 'user__username')
    list_filter = ('status', 'timestamp')
    readonly_fields = ('timestamp', 'details_preview')

    fieldsets = (
        ('📋 Основное', {
            'fields': ('user', 'action', 'status'),
            'description': 'Основная информация о событии'
        }),
        ('🕒 Временные метки', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
        ('📁 Детали', {
            'fields': ('details_preview',),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        if obj.user:
            return format_html(
                "{}<br>📞 {}",
                obj.user.username,
                obj.user.phone_number
            )
        return "Системное событие"
    user_info.short_description = "Пользователь"

    def status_badge(self, obj):
        colors = {
            0: '#9E9E9E',
            200:  '#4CAF50',
            201:  '#4CAF50',
            404: '#F44336',
            403: '#00f1f1',
            400: '#F44336',
            500: '#F44336',
            402: '#F44336',
            401: '#F44336',
            302: '#00f1f1',
        }
        return format_html(
            '<span style="color: {};">●</span> {}',
            colors.get(obj.status, '#9E9E9E'),
            self.get_status_display(obj.status)
        )
    status_badge.short_description = "Статус"

    def details_preview(self, obj):
        return format_html("<pre>{}</pre>", json.dumps(obj.details, indent=2))
    details_preview.short_description = "Детали"

    def get_status_display(self, status):
        return {
            0: 'Не определён',
            200: 'Успех',
            201: 'Успех',
            404: 'Не найдено',
            403: 'Нет доступа',
            400: 'Внутреняя ошибка сервера',
            500: 'Критическая ошибка сервера',
            402: 'Ошибка',
            401: 'Ошибка',
            302: 'Предупреждение',
        }.get(status, 'Неизвестно')