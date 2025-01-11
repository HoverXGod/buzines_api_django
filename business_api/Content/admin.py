from django.contrib import admin
from .models import Post, PageText

@admin.register(Post)
class ContetnAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'text', 'title', 'created_at', 'updated_at', 'images']
    search_fields = ['id', 'author__username', 'key_value', 'is_active']
    readonly_fields = ['id', 'author', 'text', 'title', 'created_at', 'updated_at', 'images']

@admin.register(PageText)
class PageTextAdmin(admin.ModelAdmin): pass
