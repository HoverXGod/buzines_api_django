from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
    list_display = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    search_fields = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']
    readonly_fields = ['id']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'description', 'image']
    search_fields = ['id', 'name', 'description', 'image']
    readonly_fields = ['id']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'product', 'time_add']
    search_fields = ['id', 'user', 'product', 'time_add']
    readonly_fields = ['id', 'user', 'product', 'time_add']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin): 
    list_display =  ['id', 'discount', 'product', 'description', 'name', 'on_start']
    search_fields = ['id', 'product', 'name', 'discount', 'on_start']
    readonly_fields = ['id']

@admin.register(PersonalDiscount)
class PersonalDiscountyAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'discount', 'product__name', 'description', 'name', 'on_start']
    search_fields = ['id', 'user', 'product', 'name', 'discount', 'on_start']
    readonly_fields = ['id']

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin): 
    list_display = ['id', 'code', 'discount']
    search_fields = ['id', 'code', 'discount']
    readonly_fields = ['id']