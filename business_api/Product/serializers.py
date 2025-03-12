from rest_framework import serializers
from .models import Category, Product, Cart
from User.serializers import UserSerializer

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