from django.contrib import admin
from .models import Payment
from admin import BaseAdmin
from django.utils.html import format_html

@admin.register(Payment)
class PaymentAdmin(BaseAdmin):
    list_display = ('id_badge', 'amount_rub', 'status_icon', 'method_icon', 'date')
    list_filter = ('status', 'method')
    search_fields = ('payment_id', 'user__phone_number')
    
    fieldsets = (
        ('💳 Основное', {
            'fields': ('method', 'status', 'cost'),
            'description': 'Информация о платежной операции'
        }),
        ('🕒 Временные метки', {
            'fields': ('created_time', 'pay_time'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_time',)

    def id_badge(self, obj):
        return format_html(
            '<span style=" #f0f0f0; padding:2px 8px; border-radius:5px;">#{}</span>',
            obj.payment_id[:6]
        )
    id_badge.short_description = "ID платежа"

    def amount_rub(self, obj):
        return f"{obj.cost} ₽"
    amount_rub.short_description = "Сумма"

    def status_icon(self, obj):
        icons = {
            'pending': '🕒 Ожидает',
            'completed': '✅ Успешно',
            'failed': '❌ Ошибка',
            'refunded': '↩️ Возврат'
        }
        return icons.get(obj.status, '')
    status_icon.short_description = "Статус"

    def method_icon(self, obj):
        icons = {
            'card': '💳 Карта',
            'cash': '💵 Наличные',
            'online': '🌐 Онлайн'
        }
        return icons.get(obj.method, '')
    method_icon.short_description = "Способ"

    def date(self, obj):
        return obj.created_time.strftime("%d.%m.%Y %H:%M")
    date.short_description = "Дата и время"