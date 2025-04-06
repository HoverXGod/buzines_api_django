from django.contrib import admin
from .models import Post, PageText
from admin import BaseAdmin
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('title', 'author_info', 'images_preview', 'dates')
    search_fields = ('title', 'text')
    list_filter = ('author',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('📝 Контент', {
            'fields': ('title', 'text', 'images'),
            'description': 'Содержимое поста'
        }),
        ('👤 Автор', {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
    )

    def author_info(self, obj):
        return format_html(
            "{}<br>📞 {}",
            obj.author.username,
            obj.author.phone_number
        )
    author_info.short_description = "Автор"

    def images_preview(self, obj):
        if obj.images:
            return format_html('<img src="{}" height="50" />', obj.images.split(',')[0])
        return "-"
    images_preview.short_description = "Превью"

    def dates(self, obj):
        return format_html(
            "Создан: {}<br>Обновлен: {}",
            obj.created_at.strftime("%d.%m.%Y"),
            obj.updated_at.strftime("%d.%m.%Y")
        )
    dates.short_description = "Даты"

# Тексты страниц
@admin.register(PageText)
class PageTextAdmin(BaseAdmin):
    list_display = ('page_name', 'index', 'text_preview')
    search_fields = ('page_name', 'index')
    list_filter = ('page_name',)

    fieldsets = (
        ('📄 Контент страницы', {
            'fields': ('page_name', 'index', 'text'),
            'description': 'Управление текстовым содержимым страниц'
        }),
    )

    def text_preview(self, obj):
        return f"{obj.text[:50]}..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Текст"
