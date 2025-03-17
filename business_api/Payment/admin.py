from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PageTextAdmin(admin.ModelAdmin): 
    list_display = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time', 'discount']
    search_fields = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time', 'discount']
    readonly_fields = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time', 'discount']
