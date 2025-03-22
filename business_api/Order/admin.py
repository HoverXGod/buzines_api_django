from django.contrib import admin
from .models import Order

@admin.register(Order)
class PageTextAdmin(admin.ModelAdmin): 
    list_display = ['id', 'payment', 'user', 'date', 'dilivery', 'products', 'dilivery_status']
    search_fields = ['id', 'payment', 'user', 'date', 'dilivery', 'products', 'dilivery_status']
    readonly_fields = ['id', 'payment', 'user', 'date', 'dilivery', 'products', 'dilivery_status']
