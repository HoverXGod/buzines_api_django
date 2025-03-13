from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
    list_display = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    search_fields = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    readonly_fields = ['index']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'description', 'image']
    search_fields = ['id', 'name', 'description', 'image']
    readonly_fields = ['index']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'product', 'time_add']
    search_fields = ['id', 'user', 'product', 'time_add']
    readonly_fields = ['id', 'user', 'product', 'time_add']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin): 
    list_display =  ['id', 'discount', 'category', 'product', 'description', 'name']
    search_fields = ['id', 'product', 'name', 'discount']
    readonly_fields = ['index']

@admin.register(PersonalDiscount)
class PersonalDiscountyAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'discount', 'category', 'product', 'description', 'name']
    search_fields = ['id', 'user', 'product', 'name', 'discount']
    readonly_fields = ['index']