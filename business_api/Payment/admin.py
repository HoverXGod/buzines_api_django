from django.contrib import admin
from .models import Product

@admin.register(Product)
class PageTextAdmin(admin.ModelAdmin): 
    list_display = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time']
    search_fields = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time']
    readonly_fields = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time']
