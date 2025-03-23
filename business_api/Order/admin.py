from django.contrib import admin
from .models import Order, SalesChannel, OrderItem
from admin import BaseAdmin
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ('id_badge', 'user_info', 'total_rub', 'status_icon', 'delivery_status')
    list_filter = ('status', 'chanell')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('📦 Основное', {
            'fields': ('user', 'status', 'chanell'),
            'description': 'Основная информация о заказе'
        }),
        ('🚚 Доставка', {
            'fields': ('delivery', 'delivery_status'),
        }),
    )

    def id_badge(self, obj):
        return format_html(
            '<span style=" #e0e0e0; padding:2px 8px; border-radius:5px;">#{}</span>',
            obj.id
        )
    id_badge.short_description = "Номер"

    def user_info(self, obj):
        return format_html(
            "{}<br>📞 {}",
            obj.user.short_name(),
            obj.user.phone_number
        )
    user_info.short_description = "Клиент"

    def total_rub(self, obj):
        return f"{obj.total} ₽"
    total_rub.short_description = "Сумма"

    def status_icon(self, obj):
        icons = {
            'new': '🆕',
            'processing': '🔄',
            'completed': '✅',
            'canceled': '❌'
        }
        return f"{icons.get(obj.status, '')} {obj.get_status_display()}"
    status_icon.short_description = "Статус"
    
@admin.register(SalesChannel)
class SalesChannelAdmin(BaseAdmin):
    list_display = ('name', 'order_count', 'last_order', 'profitability')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('📡 Канал', {
            'fields': ('name', 'description'),
            'description': 'Управление каналами продаж'
        }),
    )

    def order_count(self, obj):
        return obj.order_set.count()
    order_count.short_description = "🛒 Заказов"

    def last_order(self, obj):
        last = obj.order_set.order_by('-date').first()
        return last.date.strftime("%d.%m.%Y") if last else "-"
    last_order.short_description = "Последний заказ"

    def profitability(self, obj):
        return "▲ 15%"  # Заглушка для примера
    profitability.short_description = "Рентабельность"
