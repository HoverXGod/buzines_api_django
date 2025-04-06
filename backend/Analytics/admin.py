from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from .forms import ProductPerformanceForm
from django.contrib.admin import SimpleListFilter
from django_json_widget.widgets import JSONEditorWidget  
from .models import *
import json, csv

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

    def has_add_permission(self, request):
        return False

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
            '<a href="/admin/Product/product/{}/change/">{}</a>',
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

@admin.register(CustomerLifetimeValue)
class CustomerLifetimeValueAdmin(admin.ModelAdmin):
    # Настройки списка записей
    list_display = (
        'id',
        'user_link',
        'total_spent_formatted',
        'annual_clv',
        'purchase_frequency_formatted',
        'preferred_category_link',
        'last_updated_formatted',
        'avg_order_value_formatted'
    )
    list_select_related = ('user', 'preferred_category')
    list_filter = (
        'preferred_category',
    )
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'user_link',
        'annual_clv',
        'avg_order_value',
        'purchase_frequency_formatted',
        'total_spent',
        'category_spend',
        'last_updated_formatted',
        'total_spent_formatted',
        'preferred_category_link',
        'avg_order_value_formatted',
    )
    ordering = ('-last_updated',)

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('user_link', 'last_updated')
        }),
        ('Финансовая аналитика', {
            'fields': (
                'total_spent_formatted',
                'avg_order_value',
                'purchase_frequency',
                'annual_clv'
            ),
            'description': 'Автоматически рассчитываемые показатели'
        }),
        ('Категорийные предпочтения', {
            'fields': ('preferred_category_link', 'category_spend'),
            'classes': ('collapse',)
        })
    )

    # Кастомные методы для отображения
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/User/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'Пользователь'

    def preferred_category_link(self, obj):
        if obj.preferred_category:
            return format_html(
            '<a href="/admin/Product/category/{}/change/">{}</a>',
            obj.preferred_category.id,
            obj.preferred_category.name
        )
        return "-"
    preferred_category_link.short_description = 'Любимая категория'

    def total_spent_formatted(self, obj):
        return f"₽{obj.total_spent}"
    total_spent_formatted.short_description = 'Всего потрачено'

    def annual_clv(self, obj):
        return f"₽{obj.calculate_clv()}/год"
    annual_clv.short_description = 'Годовая ценность'

    def avg_order_value_formatted(self, obj):
        return f"₽{obj.avg_order_value}"
    avg_order_value_formatted.short_description = 'Средний чек'  

    def last_updated_formatted(self, obj):
        return f"₽{obj.last_updated}"
    last_updated_formatted.short_description = 'Последние обновление' 

    def purchase_frequency_formatted(self, obj):
        return f"₽{obj.purchase_frequency}"
    purchase_frequency_formatted.short_description = 'Частота покупок'

    # Запрет ручного создания записей
    def has_add_permission(self, request):
        return False

    # Автоматическое обновление данных при открытии
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            obj = self.get_object(request, object_id)
            if obj:
                CustomerLifetimeValue.objects.update_clv(obj.user)
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    def get_chart_config(self, request):
        
        return {
            'charts': [
                {
                    'title': 'Прибавка клиентов за последние 30 дней',
                    'type': 'line',  # line, bar, pie и др.
                    'data_source': 'get_charts',  # Имя метода, возвращающего данные
                    'x_axis': 'date_joined',
                    'y_axis': 'total',
                }
            ]
        }
    
    def get_charts(self):
        return_data = CustomerBehavior.objects.filter(
            user__date_joined=timezone.now() - timedelta(days=30)
        ).values('user__date_joined').annotate(
            total=Count('date_joined')
        ).order_by(
            'date_joined'
        )
        print(return_data)

        print(1)
        return return_data

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    form = ProductPerformanceForm
    list_display = ('product', 'date', 'get_category_name', 'total_units_sold', 
                   'conversion_rate_display', 'price_indicator', 'stock_status')
    list_filter = ('date', 'product__category__name', 'product__is_active')
    search_fields = ('product__name', 'category__name')
    autocomplete_fields = ['product']
    readonly_fields = ('conversion_rate_display', 'get_category_name', 'stock_status', 'price_indicator')
    actions = ['update_metrics_action', 'recalculate_conversion']

    fieldsets = (
        ("Основная информация", {
            'fields': ('product', 'date', 'get_category_name')
        }),
        ("Поведение пользователей", {
            'fields': ('views', 'cart_adds', 'purchases'),
            'description': "Данные о взаимодействии пользователей с товаром"
        }),
        ("Складские показатели", {
            'fields': ('stock_level', 'stock_status'),
            'classes': ('collapse',)
        }),
        ("Финансовые метрики", {
            'fields': ('total_units_sold', 'avg_selling_price', 
                      'discount_impact', 'price_indicator'),
            'classes': ('wide',)
        })
    )

    @admin.display(description='Категория')
    def get_category_name(self, obj):
        if obj.product and obj.product.category:
            return obj.product.category.name
        return 'Не указана'

    # Кастомные поля для отображения
    def conversion_rate_display(self, obj):
        return f"{obj.metrics.get('conversion_rate', 0)}%"
    conversion_rate_display.short_description = "Коэффициент конверсии"

    def stock_status(self, obj):
        stock = obj.metrics.get('stock_level', 0)
        if stock == 0:
            return mark_safe('<span style="color: red;">Нет в наличии</span>')
        elif stock < 6:
            return mark_safe(f'<span style="color: orange;">Мало ({stock})</span>')
        return mark_safe(f'<span style="color: green;">В наличии ({stock})</span>')
    stock_status.short_description = "Статус запасов"

    def price_indicator(self, obj):
        return f"▲ {obj.avg_selling_price}" if obj.discount_impact == 0 else f"▼ {obj.avg_selling_price}"
    price_indicator.short_description = "Динамика цены"

    # Кастомные действия
    @admin.action(description="Обновить метрики из заказов")
    def update_metrics_action(self, request, queryset):
        for obj in queryset:
            obj.update_metrics()
            obj.save()
        self.message_user(request, f"Обновлено {queryset.count()} записей")

    @admin.action(description="Пересчитать коэффициент конверсии")
    def recalculate_conversion(self, request, queryset):
        for obj in queryset:
            obj.update_conversion_rate()
            obj.save()
        self.message_user(request, f"Пересчитано для {queryset.count()} записей")

    # Валидация и подсказки
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании
            return self.readonly_fields + ('product', 'date')
        return self.readonly_fields

    # Визуальные улучшения
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_instructions'] = True
        return super().add_view(request, form_url, extra_context)

@admin.register(CohortAnalysis)
class CohortAnalysisAdmin(admin.ModelAdmin):
    # Настройки отображения списка
    list_display = [
        'cohort_date_formatted',
        'retention_day',
        'primary_category_display',
        'total_users',
        'active_users',
        'retention_rate_bar',
        'revenue_formatted'
    ]
    
    list_filter = [
        ('cohort_date', admin.DateFieldListFilter),
        'retention_day',
        'primary_category'
    ]
    
    search_fields = ['primary_category__name']
    
    # Настройки детального просмотра
    fieldsets = (
        ('Основные параметры', {
            'fields': (
                'cohort_date', 
                'retention_day', 
                'primary_category'
            ),
            'description': '<h4>Основные параметры когорты</h4>'
        }),
        ('Показатели эффективности', {
            'fields': ('metrics_display',),
            'classes': ('collapse',),
            'description': '''
                <h4>Метрики эффективности</h4>
            '''
        }),
    )
    
    readonly_fields = ['metrics_display']
    actions = ['export_as_csv', 'refresh_metrics']

    # Кастомные методы для отображения
    def cohort_date_formatted(self, obj):
        return obj.cohort_date.strftime("%d %b %Y")
    cohort_date_formatted.short_description = 'Дата когорты'
    cohort_date_formatted.admin_order_field = 'cohort_date'

    def primary_category_display(self, obj):
        return obj.primary_category.name if obj.primary_category else 'Без категории'
    primary_category_display.short_description = 'Основная категория'

    def total_users(self, obj):
        return obj.metrics.get('total_users', 0)
    total_users.short_description = 'Пользователи'

    def active_users(self, obj):
        return obj.metrics.get('active_users', 0)
    active_users.short_description = 'Активные'

    def retention_rate_bar(self, obj):
        rate = obj.retention_rate
        color = "green" if rate > 60 else "orange" if rate > 30 else "red"
        s = f'<div style="background:{color}; width:{rate}%">{rate:.1f}%</div>'
        return format_html(s)
    retention_rate_bar.short_description = 'Удержание'
    retention_rate_bar.admin_order_field = 'metrics__active_users'

    def revenue_formatted(self, obj):
        return f"{obj.metrics.get('revenue', 0):,.2f} ₽"
    revenue_formatted.short_description = 'Выручка'

    def metrics_display(self, obj):
        metrics = obj.metrics
        return format_html(
            f'''
            <table style='border-collapse: collapse' class="metrics-table">
                <tr><td>Средний чек</td><td>{metrics.get('avg_order_value', 0):.2f} ₽</td></tr>
                <tr><td>Повторные покупки</td><td>{metrics.get('repeat_purchases', 0)}</td></tr>
                <tr><td>Конверсия</td><td>{metrics.get('conversion_rate', 0):.1f}%</td></tr>
            </table> '''
        )
    metrics_display.short_description = 'Детализация метрик'

    # Действия
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name}.csv'
        
        writer = csv.writer(response)
        writer.writerow([
            'Дата когорты', 
            'День удержания', 
            'Категория',
            'Пользователи',
            'Активные',
            'Удержание (%)',
            'Выручка'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.cohort_date.strftime("%Y-%m-%d"),
                obj.retention_day,
                obj.primary_category.name if obj.primary_category else '',
                obj.metrics.get('total_users', 0),
                obj.metrics.get('active_users', 0),
                f"{obj.retention_rate:.1f}%",
                obj.metrics.get('revenue', 0)
            ])
        
        return response
    export_as_csv.short_description = 'Экспорт выбранного в CSV'

    def refresh_metrics(self, request, queryset):
        for obj in queryset:
            obj.refresh_metrics()
        self.message_user(request, f"Обновлено {queryset.count()} записей")
    refresh_metrics.short_description = 'Обновить метрики для выбранных когорт'

    # Настройки интерфейса
    date_hierarchy = 'cohort_date'
    list_per_page = 50
    list_max_show_all = 200
    show_full_result_count = False
    preserve_filters = True

    class Media:
        css = {
            'all': ('admin/css/cohort_analysis.css',)
        }

@admin.register(PaymentAnalysis)
class PaymentAnalysisAdmin(admin.ModelAdmin):
    # Отображение списка
    list_display = [
        'id',
        'payment_link',
        'payment_status',
        'risk_level',
        'chargeback_probability_bar',
        'gateway_performance_formatted',
        'analysis_date'
    ]
    
    list_filter = [
        ('analysis_timestamp', admin.DateFieldListFilter),
    ]
    
    search_fields = ['payment__payment_id', 'payment__user__email']
    
    # Детальный просмотр
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'payment_link',
                'analysis_date'
            ),
            'classes': ('wide',)
        }),
        ('Оценка рисков', {
            'fields': (
                'risk_level',
                'chargeback_probability_bar',
                'fraud_indicators_display'
            ),
            'classes': ('collapse', 'wide')
        }),
        ('Технические показатели', {
            'fields': ('gateway_performance_formatted',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'payment_link',
        'risk_level',
        'chargeback_probability_bar',
        'fraud_indicators_display',
        'gateway_performance_formatted',
        'analysis_date',
    ]
    
    actions = ['flag_for_review']
    
    # Кастомные методы
    def payment_link(self, obj): 
        return obj.payment.payment_id
    payment_link.short_description = 'Платеж'
    
    def payment_status(self, obj):
        status_colors = {
            'completed': 'green',
            'failed': 'red',
            'refunded': 'orange'
        }
        color = status_colors.get(obj.payment.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color,
            obj.payment.get_status_display()
        )
    payment_status.short_description = 'Статус'
    
    def risk_level(self, obj):
        colors = {
            'Низкий': '#4CAF50',
            'Умеренный': '#FFC107',
            'Высокий': '#F44336',
            'Критический': '#9C27B0'
        }
        return format_html(
            '<div style="background:{}; color: white; padding: 2px 8px; border-radius: 4px; text-align: center;">{}</div>',
            colors[obj.risk_category],
            obj.risk_category
        )
    risk_level.short_description = 'Уровень риска'
    
    def chargeback_probability_bar(self, obj):
        width = min(obj.chargeback_probability, 100)
        color = '#f44336' if width > 50 else '#ff9800' if width > 30 else '#4caf50'
        return format_html(
            f'<div style="background:{color}; width: {width}%; color: white; padding: 2px; border-radius: 3px; text-align: center;">{obj.chargeback_probability:.1f}%</div>')
    chargeback_probability_bar.short_description = 'Вероятность возврата'
    
    def fraud_indicators_display(self, obj):
        indicators = []
        icons = {
            'high_amount': '💰',
            'currency_mismatch': '🌍',
            'multiple_attempts': '🔄',
            'non_working_hours': '🌙'
        }
        
        for indicator, value in obj.fraud_indicators.items():
            if value:
                indicators.append(f"{icons.get(indicator, '⚠️')} {indicator.replace('_', ' ').title()}")
        
        return format_html(
            '<div style="column-count: 2; column-gap: 20px;">{}</div>',
            '<br>'.join(indicators) if indicators else 'Нет признаков мошенничества'
        )
    fraud_indicators_display.short_description = 'Признаки мошенничества'
    
    def gateway_performance_formatted(self, obj):
        if obj.gateway_performance:
            if obj.gateway_performance > 10:
                color = 'red'
            elif obj.gateway_performance > 5:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {};">{:.2f} сек</span>',
                color,
                obj.gateway_performance
            )
        return 'N/A'
    gateway_performance_formatted.short_description = 'Скорость обработки'
    
    def flag_for_review(self, request, queryset):
        for obj in queryset:
            obj.payment.needs_review = True
            obj.payment.save()
        self.message_user(request, f"{queryset.count()} платежей отправлено на проверку")
    flag_for_review.short_description = 'Пометить для проверки'


    # Настройки интерфейса
    date_hierarchy = 'analysis_timestamp'
    list_per_page = 25
    ordering = ['-analysis_timestamp']
    
    class Media:
        css = {
            'all': ('admin/css/payment_analysis.css',)
        }

@admin.register(OrderAnalytics)
class OrderAnalyticsAdmin(admin.ModelAdmin):
    # Настройки списка
    list_display = [
        'order_link',
        'margin_display',
        'acquisition_source',
        'churn_risk_level',
        'top_products',
        'basket_diversity'
    ]
    
    list_filter = [
        'acquisition_source',
        ('order__date', admin.DateFieldListFilter)
    ]
    
    search_fields = ['order__id', 'order__user__email']
    
    # Детальный просмотр
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'order_link',
                'margin_display',
                'acquisition_source'
            ),
            'classes': ('wide',)
        }),
        ('Прогнозы и риски', {
            'fields': (
                'churn_risk_level',
                'customer_journey_display'
            ),
            'classes': ('collapse',)
        }),
        ('Товарная аналитика', {
            'fields': (
                'basket_diversity',
            ),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = [
        'order_link',
        'margin_display',
        'churn_risk_level',
        'customer_journey_display',
        'basket_diversity'
    ]
    
    actions = ['recalculate_metrics']
    
    # Кастомные методы
    def order_link(self, obj):
        return obj.order.id
    order_link.short_description = 'Заказ'
    
    def margin_display(self, obj):
        color = '#4CAF50' if obj.margin > 0 else '#F44336'
        return format_html(
            f'<div style="color: {color};">{obj.margin} ₽ ({obj.margin_percentage:.1f}%)</div>'
        )
    margin_display.short_description = 'Маржинальность'
    
    def churn_risk_level(self, obj):
        colors = {
            'low': '#4CAF50',
            'medium': '#FFC107',
            'high': '#F44336'
        }
        risk_level = 'low' if obj.predicted_churn_risk < 30 else 'medium' if obj.predicted_churn_risk < 70 else 'high'
        return format_html(
            f'<div style="background: {colors[risk_level]}; color: white; padding: 2px 8px; border-radius: 4px;">{obj.predicted_churn_risk:.1f}%</div>'    
        )
    churn_risk_level.short_description = 'Риск оттока'
    
    def top_products(self, obj):
        products = obj.item_metrics.get('top_items', [])[:3]
        return ", ".join([f"{p['product__name']} ({p['total_units']})" for p in products]) or 'Нет данных'
    top_products.short_description = 'Топ товаров'
    
    def basket_diversity(self, obj):
        diversity = obj.item_metrics.get('basket_diversity', 0)
        return format_html(
            f'''<div style="width: 100px; height: 20px; background: #eee; border-radius: 10px;">
            <div style="width: { diversity * 100}%; height: 100%; background: #2196F3; border-radius: 10px;"></div></div>
            <div>{diversity:.0%}</div>'''
        )
    basket_diversity.short_description = 'Разнообразие'
    
    def customer_journey_display(self, obj):
        journey = obj.customer_journey
        items = []
        if journey.get('days_to_first_order'):
            items.append(f"Первый заказ через: {journey['days_to_first_order']} дней")
        if journey.get('pre_order_visits'):
            items.append(f"Визитов перед заказом: {journey['pre_order_visits']}")
        if journey.get('total_orders'):
            items.append(f"Всего заказов: {journey['total_orders']}")
        
        br = '<br>'
        
        return format_html(
            f'<div style="column-count: 2; column-gap: 30px;">{ br.join(items) }</div>'    
        )
    customer_journey_display.short_description = 'Поведение покупателя'
    
    def recalculate_metrics(self, request, queryset):
        for obj in queryset:
            OrderAnalytics.objects.add_entry(obj.order)
        self.message_user(request, f"Обновлено {queryset.count()} записей")
    recalculate_metrics.short_description = 'Пересчитать метрики'
    
    # Настройки интерфейса
    date_hierarchy = 'order__date'
    list_per_page = 30
    list_select_related = True
    show_full_result_count = False
    
    class Media:
        css = {
            'all': ('admin/css/order_analytics.css',)
        }

@admin.register(InventoryTurnover)
class InventoryTurnoverAdmin(admin.ModelAdmin):
    # Группировка полей для удобства ввода
    fieldsets = ( ('Основная информация', {
            'fields': (
                'product', 
                'category',
                ('period_start', 'period_end') )
            }
        ),
        ('Показатели эффективности', {
            'fields': (
                'stock_turnover',
                'stockout_days',
                'demand_forecast'
            ),
            'description': 'Расчетные показатели эффективности запасов'
        }),
    )

    # Автозаполнение категории при выборе товара
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            try:
                product_id = request.GET.get('product')
                if product_id:
                    product = Product.objects.get(id=product_id)
                    kwargs["queryset"] = Category.objects.filter(id=product.category.id)
            except:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Настройка отображения списка
    list_display = (
        'product_link',
        'category',
        'period',
        'stock_turnover_bar',
        'stockout_days',
        'demand_forecast'
    )
    
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter),
    )
    
    search_fields = ('product__name', 'category__name')
    
    readonly_fields = ('category', 'period_end', 'stock_turnover', 'stockout_days', 'demand_forecast')
    
    actions = ['recalculate_turnover']

    # Кастомные методы для отображения
    def product_link(self, obj):
        url = f'admin/Product/product/{obj.product.id}/change'
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Товар'

    def period(self, obj):
        return f"{obj.period_start.strftime('%b %Y')}"
    period.short_description = 'Период'

    def stock_turnover_bar(self, obj):
        value = min(int(obj.stock_turnover * 20), 100)
        return format_html(
            '<div style="width: 100px; height: 20px; background: #ddd">'
            '<div style="width: {}%; height: 100%; background: {};"></div></div>',
            value, '#4CAF50' if obj.stock_turnover > 0.5 else '#FF5722'
        )
    stock_turnover_bar.short_description = 'Оборачиваемость'

    # Действия
    def recalculate_turnover(self, request, queryset):
        for item in queryset:
            item.product.calculate_turnover()
        self.message_user(request, f"Пересчет выполнен для {queryset.count()} записей")
    recalculate_turnover.short_description = "Пересчитать показатели"

# Фильтр по месяцам для периода
class PeriodMonthFilter(SimpleListFilter):
    title = 'Месяц периода'
    parameter_name = 'period_month'

    def lookups(self, request, model_admin):
        return (
            ('current', 'Текущий месяц'),
            ('last', 'Прошлый месяц'),
            ('3m', 'Последние 3 месяца'),
        )

    def queryset(self, request, queryset):
        now = timezone.now().date()
        if self.value() == 'current':
            return queryset.filter(period_start__month=now.month)
        if self.value() == 'last':
            last_month = now.replace(day=1) - timedelta(days=1)
            return queryset.filter(period_start__month=last_month.month)
        if self.value() == '3m':
            three_months_ago = now - timedelta(days=90)
            return queryset.filter(period_start__gte=three_months_ago)

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'product_link',
        'change_type_icon',
        'stock_changes',
        'date',
    )
    
    list_filter = (
        'change_type',
        ('date', admin.DateFieldListFilter),
    )
    
    search_fields = ('product__name',)
    
    readonly_fields = ('previous_stock', 'new_stock', 'date')
    
    fieldsets = (
        ('Информация о товаре', {
            'fields': ('product',)
        }),
        ('Изменения запасов', {
            'fields': (
                ('previous_stock', 'new_stock'),
                'quantity',
                'change_type'
            )
        }),
        ('Дополнительно', {
            'fields': ('date', 'notes'),
            'classes': ('collapse',)
        }),
    )

    def product_link(self, obj):
        url = f'admin/Product/product/{obj.product.id}/change'
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Товар'

    def change_type_icon(self, obj):
        icons = {
            'sale': '🛒',
            'restock': '📦',
            'adjustment': '✏️'
        }
        return f"{icons[obj.change_type]} {obj.get_change_type_display()}"
    change_type_icon.short_description = 'Тип изменения'

    def stock_changes(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<span style="color: #888;">{}</span>'
            '<span style="font-size: 18px;">→</span>'
            '<span style="color: {};">{}</span></div>',
            obj.previous_stock,
            '#4CAF50' if obj.new_stock > obj.previous_stock else '#FF5722',
            obj.new_stock
        )
    stock_changes.short_description = 'Изменение запасов'

@admin.register(OrderItemAnalytics)
class OrderItemAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'order_item_info',
        'margin_display',
        'profitability_index_display',
        'delivery_status',
        'popularity_badge',
        'return_rate_display',
        'cross_sell_count'
    ]
    
    list_filter = [
        'delivery_time',
        'cross_sell_products'
    ]
    
    search_fields = [
        'order_item__product__name',
        'order_item__order__user__email'
    ]
    
    fieldsets = (
        ('Финансовые показатели', {
            'fields': ('margin', 'profitability_index'),
            'description': '💰 <strong>Экономические метрики товара:</strong>'
        }),
        ('Логистика', {
            'fields': ('delivery_time',),
            'description': '🚚 <strong>Данные о доставке:</strong>'
        }),
        ('Поведенческие метрики', {
            'fields': ('popularity_score', 'return_rate'),
            'description': '📊 <strong>Аналитика спроса и возвратов:</strong>'
        }),
        ('Рекомендации', {
            'fields': ('cross_sell_products',),
            'description': '🛍️ <strong>Сопутствующие товары:</strong>'
        })
    )
    
    filter_horizontal = ['cross_sell_products']
    readonly_fields = ['last_updated']
    actions = ['update_metrics']
    list_per_page = 30
    list_select_related = ['order_item', 'order_item__product']
    
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
                'admin/css/analytics.css'
            )
        }

    @admin.display(description='Товар в заказе')
    def order_item_info(self, obj):
        product = obj.order_item.product
        return format_html((
            '<div class="product-card">'
            '<i class="fas fa-box-open"></i>'
            '<div>'
            '<h4>{}</h4>'
            '<small>Заказ #{} · {} шт</small>'
            '</div>'
            '</div>',
            product.name,
            obj.order_item.order.id,
            obj.order_item.quantity
            )
        )

    @admin.display(description='Маржа', ordering='margin')
    def margin_display(self, obj):
        return format_html(
            '<div class="money-cell {}">{:.2f} ₽</div>',
            'positive' if obj.margin > 0 else 'negative',
            obj.margin
        )

    @admin.display(description='Рентабельность', ordering='profitability_index')
    def profitability_index_display(self, obj):
        return format_html(
            '<div class="progress-bar">'
            '<div class="progress-fill" style="width: {}%">{:.1f}%</div>'
            '</div>',
            min(obj.profitability_index, 100),
            obj.profitability_index
        )

    @admin.display(description='Доставка', ordering='delivery_time')
    def delivery_status(self, obj):
        if obj.delivery_time <= 3:
            icon = 'fa-rocket'
            text = 'Экспресс'
            color = 'green'
        elif obj.delivery_time <= 7:
            icon = 'fa-truck'
            text = 'Стандарт'
            color = 'orange'
        else:
            icon = 'fa-clock'
            text = 'Долгая'
            color = 'red'
        
        return format_html(
            '<div class="delivery-badge {}">'
            '<i class="fas {}"></i>{}'
            '</div>',
            color,
            icon,
            text
        )

    @admin.display(description='Популярность', ordering='popularity_score')
    def popularity_badge(self, obj):
        return format_html(
            '<div class="popularity-rating">'
            '<i class="fas fa-fire"></i>'
            '<span>{:.1f}/10</span>'
            '</div>',
            obj.popularity_score
        )

    @admin.display(description='Возвраты')
    def return_rate_display(self, obj):
        return format_html(
            '<div class="return-meter" data-value="{}">{:.1f}%</div>',
            obj.return_rate,
            obj.return_rate
        )

    @admin.display(description='Сопутствующие')
    def cross_sell_count(self, obj):
        count = obj.cross_sell_products.count()
        return format_html(
            '<div class="cross-sell-count">'
            '<i class="fas fa-link"></i>{}'
            '</div>',
            count
        )

    @admin.action(description='🔄 Обновить метрики')
    def update_metrics(self, request, queryset):
        for analytics in queryset:
            analytics.update_popularity()
            analytics.update_return_rate()
        self.message_user(request, f"Обновлено {queryset.count()} записей")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('cross_sell_products')
    
@admin.register(CustomerBehavior)
class CustomerBehaviorAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = [
        'user_email',
        'last_activity',
        'page_views',
        'cart_actions',
        'engagement_score',
        'preferences_summary'
    ]
    
    # Фильтры и поиск
    list_filter = ['user__is_staff', 'last_activity']
    search_fields = ['user__email', 'user__first_name']
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'last_activity',
            ),
            'description': 'Базовая информация о пользователе и времени активности'
        }),
        ('Метрики сессии', {
            'fields': ('session_metrics',),
            'description': '📊 <strong>Статистика взаимодействия:</strong> просмотры страниц, '
                         'время на сайте, действия с корзиной'
        }),
        ('Профиль предпочтений', {
            'fields': ('preference_profile',),
            'description': '💡 <strong>Персональные настройки:</strong> оценка вовлеченности, '
                         'предпочтения пользователя'
        }),
    )
    
    # Виджеты для JSON-полей
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(mode='tree')},
    }
    
    # Автодополнение связанных полей
    autocomplete_fields = ['user']
    
    # Поля только для чтения
    readonly_fields = ['last_activity']
    
    # Действия в списке
    actions = ['update_engagement_scores']
    
    # Настройки интерфейса
    list_per_page = 25
    show_full_result_count = False
    date_hierarchy = 'last_activity'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    # Кастомные колонки в списке
    @admin.display(description='Email пользователя', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email
    
    @admin.display(description='📈 Вовлеченность')
    def engagement_score(self, obj):
        score = obj.preference_profile.get('engagement_score', 0)
        color = 'green' if score > 50 else 'orange' if score > 20 else 'red'
        return format_html(
            '<div style="background: {}; color: white; padding: 2px 5px; border-radius: 3px; text-align: center;">{:.1f}</div>',
            color,
            score
        )
    
    @admin.display(description='📄 Просмотры')
    def page_views(self, obj):
        return obj.session_metrics.get('page_views', 0)
    
    @admin.display(description='🛒 Действия')
    def cart_actions(self, obj):
        return obj.session_metrics.get('cart_actions', 0)
    
    @admin.display(description='⚙️ Настройки')
    def preferences_summary(self, obj):
        return ', '.join([f"{k}: {v}" for k, v in obj.preference_profile.items()])
    
    # Кастомные действия
    @admin.action(description='🔄 Пересчитать вовлеченность')
    def update_engagement_scores(self, request, queryset):
        CustomerBehavior.objects.update_engagement_scores(queryset=queryset)
        self.message_user(request, f"Обновлено {queryset.count()} записей")
    
    # Улучшенные подсказки
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].help_text = "Выберите пользователя из системы"
        form.base_fields['session_metrics'].help_text = "Данные автоматически собираются системой"
        return form

    # Иконка приложения
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }