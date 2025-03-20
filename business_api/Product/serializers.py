from rest_framework import serializers
from .models import *
from User.serializers import UserSerializer, UserGroupSerializer

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']

class ProductSerializer(serializers.ModelSerializer): 

    category = CategorySerializer()
    
    class Meta:
        model = Product
        fields = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category']

class CartSerializer(serializers.ModelSerializer):

    user = UserSerializer
    product = ProductSerializer        

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'time_add']

class UserCartSerializer(serializers.ModelSerializer):

    product = ProductSerializer        

    class Meta:
        model = Cart
        fields = ['id', 'product', 'time_add']

class ProductCartSerializer(serializers.ModelSerializer):

    user = UserSerializer        

    class Meta:
        model = Cart
        fields = ['id', 'user', 'time_add']

class PromotionSerializer(serializers.ModelSerializer):

    product = ProductSerializer
    category = CategorySerializer

    class Meta:
        model = Promotion
        fields = ['id', 'discount', 'product', 'description', 'name', 'on_start']

class PersonalDiscountSerializer(serializers.ModelSerializer):
    
    user = UserSerializer
    product = ProductSerializer
    category = CategorySerializer

    class Meta:
        model = PersonalDiscount
        fields = ['id', 'user', 'discount', 'product', 'description', 'name', 'on_start']

class PromoCodeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promocode
        fields = ['id', 'code', 'discount']

class GroupPromotionSerializer(serializers.ModelSerializer):

    user_group = UserGroupSerializer
    
    class Meta:
        model = GroupPromotion
        fields = ['id', 'user_group', 'discount', 'product', 'description', 'name', 'on_start']
