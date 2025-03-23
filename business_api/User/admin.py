from django.contrib import admin
from .models import User, UserGroupItem, UserGroup
from admin import BaseAdmin
from django.utils.html import format_html

@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = ('phone_icon', 'short_name', 'order_count', 'status_badge')
    search_fields = ('phone_number', 'email')
    
    fieldsets = (
        ('📱 Контакты', {
            'fields': ('phone_number', 'email'),
            'description': 'Основные контактные данные'
        }),
        ('👤 Личные данные', {
            'fields': ('first_name', 'last_name', 'address')
        }),
        ('🔐 Права доступа', {
            'fields': ('is_active', 'is_staff'),
            'classes': ('collapse',)
        }),
    )

    def phone_icon(self, obj):
        return format_html('📞 {}', obj.phone_number)
    phone_icon.short_description = 'Телефон'

    def short_name(self, obj):
        return f"{obj.last_name} {obj.first_name[0]}." if obj.first_name else "-"
    short_name.short_description = "Имя"

    def order_count(self, obj):
        return obj.orders.count()
    order_count.short_description = "🛒 Заказов"

    def status_badge(self, obj):
        color = 'green' if obj.is_active else 'red'
        return format_html(
            '<span style="color:{};">●</span> {}',
            color,
            "Активен" if obj.is_active else "Заблокирован"
        )
    status_badge.short_description = "Статус"

class UserGroupItemInline(admin.TabularInline):
    model = UserGroupItem
    extra = 0
    fields = ('user_badge', 'time_add')
    readonly_fields = ('user_badge', 'time_add')

    def user_badge(self, obj):
        return format_html(
            "{} 📞 {}",
            obj.user.short_name(),
            obj.user.phone_number
        )
    user_badge.short_description = "Пользователь"


@admin.register(UserGroup)
class UserGroupAdmin(BaseAdmin):
    list_display = ('name', 'member_count', 'created_date', 'activity_status')
    inlines = [UserGroupItemInline]
    
    fieldsets = (
        ('👥 Группа', {
            'fields': ('name', 'description'),
            'description': 'Управление группами пользователей'
        }),
    )

    def member_count(self, obj):
        return obj.usergroupitem_set.count()
    member_count.short_description = "👤 Участников"

    def created_date(self, obj):
        first_item = obj.usergroupitem_set.first()
        return first_item.time_add.strftime("%d.%m.%Y") if first_item else "-"
    created_date.short_description = "Дата создания"

    def activity_status(self, obj):
        return "🟢 Активна" if obj.usergroupitem_set.exists() else "⚪ Не активна"
    activity_status.short_description = "Активность"


