from django.contrib import admin
from .models import Product

@admin.register(Product)
class PageTextAdmin(admin.ModelAdmin): 
    list_display = ['*']
    search_fields = ['*']
    readonly_fields = ['index']
