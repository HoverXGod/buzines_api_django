from django.contrib import admin
from .models import Api_key

@admin.register(Api_key)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'key_name', 'key_value', 'created_at', 'updated_at', 'help_text', 'is_active']
    search_fields = ['id', 'user__username', 'key_value', 'is_active']
    readonly_fields = ['id', 'user', 'key_name', 'key_value', 'created_at', 'updated_at', 'help_text', 'is_active']
