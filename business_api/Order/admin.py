from django.contrib import admin
from .models import Product

@admin.register(Product)
class PageTextAdmin(admin.ModelAdmin): 
    list_display = ['id', 'payment', 'user', 'date', 'dilivery', 'products']
    search_fields = ['id', 'payment', 'user', 'date', 'dilivery', 'products']
    readonly_fields = ['id', 'payment', 'user', 'date', 'dilivery', 'products']
