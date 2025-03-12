from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class ProductAdmin(admin.ModelAdmin): 
    list_display = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    search_fields = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    readonly_fields = ['index']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'description', 'image']
    search_fields = ['id', 'name', 'description', 'image']
    readonly_fields = ['index']