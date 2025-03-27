from django.contrib import admin
from django.utils.html import format_html
from .models import SalesFunnel
import json

@admin.register(SalesFunnel)
class SalesFunnelAdmin(admin.ModelAdmin):
    list_display = (
        'user_info', 
        'product_link', 
        'stage_badge', 
        'time_info', 
        'device_icon',
        'conversion_time'
    )
    list_filter = ('stage', 'device_type', 'category')
    search_fields = (
        'user__username', 
        'product__name',
        'category__name'
    )
    readonly_fields = (
        'timestamp', 
        'session_data_preview',
        'conversion_time_calculated'
    )
    date_hierarchy = 'timestamp'
    list_select_related = ('user', 'product', 'category')

    fieldsets = (
        ('👤 Основное', {
            'fields': ('user', 'product', 'category', 'stage'),
            'description': 'Основные параметры воронки продаж'
        }),
        ('📱 Устройство и сессия', {
            'fields': ('device_type', 'session_data_preview'),
            'classes': ('collapse',)
        }),
        ('🕒 Временные метки', {
            'fields': ('timestamp', 'conversion_time_calculated'),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        if not obj.user:
            return "Анонимный пользователь"
        return format_html(
            "{}<br>📞 {}<br><span style='color:#888'>{}</span>",
            obj.user.get_full_name() or obj.user.username,
            obj.user.phone_number,
            obj.user.email
        )
    user_info.short_description = "Пользователь"

    def product_link(self, obj):
        if not obj.product:
            return "-"
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = "Товар"

    def stage_badge(self, obj):
        colors = {
            'view': '#9E9E9E',
            'cart': '#2196F3',
            'checkout': '#FF9800',
            'payment': '#4CAF50',
            'delivery': '#673AB7'
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 6px; border-radius:4px">{}</span>',
            colors.get(obj.stage, '#607D8B'),
            obj.get_stage_display()
        )
    stage_badge.short_description = "Этап"

    def time_info(self, obj):
        return obj.timestamp.strftime("%d.%m.%Y %H:%M")
    time_info.short_description = "Дата/время"

    def device_icon(self, obj):
        icons = {
            'mobile': '📱',
            'desktop': '💻',
            'tablet': '⌨️'
        }
        return format_html(
            '{} {}',
            icons.get(obj.device_type, '❓'),
            obj.get_device_type_display()
        )
    device_icon.short_description = "Устройство"

    def conversion_time(self, obj):
        next_stage = {
            'cart': 'view',
            'checkout': 'cart',
            'payment': 'view',
            'delivery': 'payment'
        }.get(obj.stage)
        
        if not next_stage:
            return "-"
            
        time = obj.get_conversion_time(next_stage)
        return str(time) if time else "Не завершено"
    conversion_time.short_description = "Время конверсии"

    def session_data_preview(self, obj):
        return format_html(
            "<pre style='max-height: 200px; overflow: auto'>{}</pre>",
            json.dumps(obj.session_data, indent=2, ensure_ascii=False)
        )
    session_data_preview.short_description = "Данные сессии"

    def conversion_time_calculated(self, obj):
        return self.conversion_time(obj)
    conversion_time_calculated.short_description = "Время до след. этапа"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'product', 
            'category',
            'order_item',
            'order_item__product'
        )