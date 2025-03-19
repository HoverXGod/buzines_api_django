from django.contrib import admin
from .models import User, UserGroupItem, UserGroup

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'date_joined', 'isModerator', 'is_superuser', 'isAdministrator', 'email', 'phone_number']
    search_fields = ['id', 'username', 'email', 'phone_number']
    readonly_fields = ['id', 'date_joined', 'username', 'first_name', 'last_name', 'email', 'phone_number']

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'permissions']
    search_fields = ['id', 'name']
    readonly_fields = ['id']

@admin.register(UserGroupItem)
class UserGroupItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'group']
    search_fields = ['id', 'user', 'group']
    readonly_fields = ['id', 'user', 'group']