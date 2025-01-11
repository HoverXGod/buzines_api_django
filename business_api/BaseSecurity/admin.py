from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'details', 'action', 'timestamp', 'status']
    search_fields = ['user__username', 'action', 'status']
    readonly_fields = ['user', 'action', 'timestamp', 'details', 'status']

