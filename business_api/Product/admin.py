from django.contrib import admin
from .models import *
from django.utils.html import format_html
from admin import BaseAdmin

@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ('image_thumb', 'name', 'price_rub', 'stock_status', 'category_badge')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')
    
    fieldsets = (
        ('📦 Основное', {
            'fields': ('name', 'category', 'price', 'is_active'),
            'description': 'Основные параметры товара'
        }),
        ('⚖️ Характеристики', {
            'fields': ('weight', 'by_weight', 'description')
        }),
        ('🖼️ Изображения', {
            'fields': ('image',)
        }),
    )

    def image_thumb(self, obj):
        return format_html('<img src="{}" height="50" />', obj.image) if obj.image else "-"
    image_thumb.short_description = "Фото"

    def price_rub(self, obj):
        return f"{obj.price} ₽"
    price_rub.short_description = "Цена"

    def stock_status(self, obj):
        return "✅ В наличии" if obj.is_active else "⛔ Нет в наличии"
    stock_status.short_description = "Наличие"

    def category_badge(self, obj):
        return format_html(
            '<span style=" #f0f0f0; padding:2px 8px; border-radius:10px;">{}</span>',
            obj.category.name
        )
    category_badge.short_description = "Категория"

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('name', 'product_count', 'image_preview', 'status_badge')
    search_fields = ('name',)
    
    fieldsets = (
        ('📁 Основное', {
            'fields': ('name', 'is_active'),
            'description': 'Основные параметры категории'
        }),
        ('🖼️ Изображение', {
            'fields': ('image',)
        }),
        ('📝 Описание', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image)
        return "-"
    image_preview.short_description = "Превью"

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = "📦 Товаров"

    def status_badge(self, obj):
        return "✅ Активна" if obj.is_active else "⛔ Скрыта"
    status_badge.short_description = "Статус"

@admin.register(Cart)
class CartAdmin(BaseAdmin):
    list_display = (
        'user_info', 
        'product_link', 
        'formatted_quantity', 
        'total_price', 
        'time_added',
        'status_badge'
    )
    list_filter = ('user', 'product')
    search_fields = ('user__phone_number', 'product__name')
    list_select_related = ('user', 'product')
    date_hierarchy = 'time_add'
    
    fieldsets = (
        ('🛒 Основная информация', {
            'fields': ('user', 'product', 'quanity'),
            'description': 'Содержимое корзины пользователя'
        }),
        ('🕒 Временные метки', {
            'fields': ('time_add',),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        return format_html(
            "{}<br>📞 {}",
            obj.user.get_full_name() or obj.user.username,
            obj.user.phone_number
        )
    user_info.short_description = "Пользователь"

    def product_link(self, obj):
        return format_html(
            '<a href="/admin/app/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = "Товар"

    def formatted_quantity(self, obj):
        return f"{obj.quanity} {'кг' if obj.product.by_weight else 'шт'}"
    formatted_quantity.short_description = "Количество"

    def total_price(self, obj):
        return f"{obj.product.price * obj.quanity:.2f} ₽"
    total_price.short_description = "Сумма"

    def time_added(self, obj):
        return obj.time_add.strftime("%d.%m.%Y %H:%M")
    time_added.short_description = "Добавлено"

    def status_badge(self, obj):
        active_cart = obj.user.cart.filter(time_add__gte=obj.time_add).exists()
        return format_html(
            '<span style="color: {};">●</span> {}',
            '#4CAF50' if active_cart else '#F44336',
            'Активна' if active_cart else 'Неактивна'
        )
    status_badge.short_description = "Статус"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'product'
        ).prefetch_related('product__category')
    
    class Media:
        css = {
            'all': ('admin/css/cart.css',)
        }


@admin.register(Promotion)
class PromotionAdmin(BaseAdmin):
    list_display = ('name', 'product_link', 'discount_badge', 'status_icon')
    search_fields = ('name', 'product__name')
    
    fieldsets = (
        ('🎁 Акция', {
            'fields': ('name', 'product', 'discount', 'on_start'),
            'description': 'Основные параметры акции'
        }),
        ('📝 Описание', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    def product_link(self, obj):
        return format_html(
            '<a href="/admin/app/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = "Товар"

    def discount_badge(self, obj):
        return format_html(
            '<span style=" #fff3e0; padding:2px 8px; border-radius:5px;">-{}%</span>',
            obj.discount
        )
    discount_badge.short_description = "Скидка"

    def status_icon(self, obj):
        return "✅ Активна" if obj.on_start else "⏸️ На паузе"
    status_icon.short_description = "Статус"

@admin.register(PersonalDiscount)
class PersonalDiscountAdmin(BaseAdmin):
    list_display = ('user_info', 'product_link', 'discount_badge', 'created_date')
    search_fields = ('user__phone_number', 'product__name')
    
    fieldsets = (
        ('🎁 Персональное предложение', {
            'fields': ('user', 'product', 'discount'),
            'description': 'Индивидуальные условия для клиента'
        }),
    )

    def user_info(self, obj):
        return format_html(
            "{}<br>📞 {}",
            obj.user.short_name(),
            obj.user.phone_number
        )
    user_info.short_description = "Клиент"

    def product_link(self, obj):
        return format_html(
            '<a href="/admin/app/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = "Товар"

    def discount_badge(self, obj):
        return format_html(
            '<span style=" #f0f4c3; padding:2px 8px; border-radius:5px;">-{}%</span>',
            obj.discount
        )
    discount_badge.short_description = "Скидка"

    def created_date(self, obj):
        return obj.created.strftime("%d.%m.%Y") if obj.created else "-"
    created_date.short_description = "Дата создания"

class PromocodeAdmin(BaseAdmin):
    list_display = ('code_badge', 'discount_percent', 'usage_count', 'active_status')
    list_editable = ('active_status',)
    search_fields = ('code',)
    
    fieldsets = (
        ('🎟️ Основное', {
            'fields': ('code', 'discount', 'is_active'),
            'description': 'Управление промокодами'
        }),
    )

    def code_badge(self, obj):
        return format_html(
            '<span style=" #ffeb3b; padding:2px 8px; border-radius:5px;">{}</span>',
            obj.code
        )
    code_badge.short_description = "Промокод"

    def discount_percent(self, obj):
        return f"-{obj.discount}%"
    discount_percent.short_description = "Скидка"

    def usage_count(self, obj):
        return obj.order_set.count()
    usage_count.short_description = "🔄 Использований"

    def active_status(self, obj):
        return "✅ Активен" if obj.is_active else "⛔ Не активен"
    active_status.short_description = "Статус"
    active_status.boolean = True

@admin.register(GroupPromotion)
class GroupPromotionAdmin(BaseAdmin):
    list_display = ('name', 'group_badge', 'discount_badge')
    search_fields = ('name', 'user_group__name')
    
    fieldsets = (
        ('🎪 Акция', {
            'fields': ('name', 'user_group', 'discount'),
            'description': 'Настройки групповой акции'
        }),
        ('📦 Товар', {
            'fields': ('product',),
        }),
    )

    def group_badge(self, obj):
        return format_html(
            '<span style=" #e3f2fd; padding:2px 8px; border-radius:5px;">{}</span>',
            obj.user_group.name
        )
    group_badge.short_description = "Группа"

    def discount_badge(self, obj):
        return format_html(
            '<span style=" #c8e6c9; padding:2px 8px; border-radius:5px;">-{}%</span>',
            obj.discount
        )
    discount_badge.short_description = "Скидка"

class PromotionInline(admin.TabularInline):
    model = Promotion
    extra = 1

class PersonalDiscountInline(admin.TabularInline):
    model = PersonalDiscount
    extra = 1