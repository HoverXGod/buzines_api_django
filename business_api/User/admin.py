from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'date_joined', 'isModerator', 'is_superuser', 'isAdministrator', 'email', 'phone_number']
    search_fields = ['id', 'username', 'email', 'phone_number']
    readonly_fields = ['id', 'date_joined', 'isModerator', 'is_superuser', 'isAdministrator', 'email', 'phone_number']
