from rest_framework import serializers
from .models import *
from User.serializers import UserSerializer, UserGroupSerializer

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'slug', 'parent', 'meta_title', 'meta_description']

class ProductSerializer(serializers.ModelSerializer): 

    category = CategorySerializer()
    
    class Meta:
        model = Product
        depth = 1
        fields = ['id', 'image', 'name', 'description', 'price', 'by_weight', 'weight', 'weight_start', 'weight_end', 'category', 'sku', 'stock', 'slug']

class CartSerializer(serializers.ModelSerializer):

    user = UserSerializer
    product = ProductSerializer        

    class Meta:
        model = Cart
        depth = 1
        fields = ['id', 'user', 'product', 'time_add']

class UserCartSerializer(serializers.ModelSerializer):

    product = ProductSerializer        

    class Meta:
        model = Cart
        depth = 1
        fields = ['id', 'product', 'time_add']

class ProductCartSerializer(serializers.ModelSerializer):

    user = UserSerializer        

    class Meta:
        model = Cart
        depth = 1
        fields = ['id', 'user', 'time_add']

class PromotionSerializer(serializers.ModelSerializer):

    product = ProductSerializer
    category = CategorySerializer

    class Meta:
        model = Promotion
        depth = 1
        fields = ['id', 'discount', 'product', 'description', 'name', 'on_start', 'start_date', 'end_date', 'used_count', 'max_usage']

class PersonalDiscountSerializer(serializers.ModelSerializer):
    
    user = UserSerializer
    product = ProductSerializer
    category = CategorySerializer

    class Meta:
        model = PersonalDiscount
        depth = 1
        fields = ['id', 'user', 'discount', 'product', 'description', 'name', 'on_start', 'start_date', 'end_date', 'used_count', 'max_usage']

class PromoCodeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promocode
        fields = ['id', 'code', 'discount']

class GroupPromotionSerializer(serializers.ModelSerializer):

    user_group = UserGroupSerializer
    
    class Meta:
        model = GroupPromotion
        depth = 1
        fields = ['id', 'user_group', 'discount', 'product', 'description', 'name', 'on_start', 'start_date', 'end_date', 'used_count', 'max_usage']

class SubscriptionSerializer(serializers.ModelSerializer):

    product = ProductSerializer

    class Meta:
        model = Subscription
        depth = 1
        fields = ['id', 'product', 'is_active', 'duration_days', 'discription']

class UserSubscriptionSerializer(serializers.ModelSerializer):

    product = ProductSerializer

    class Meta:
        model = Subscription
        depth = 2
        fields = ['id', 'product', 'is_active', 'duration_days', 'description']

class UserSubscriptionItemSerializer(serializers.ModelSerializer):

    subscription = SubscriptionSerializer
    user = UserSerializer

    class Meta:
        model = UserSubscriptionItem
        depth = 2
        fields = ['id', 'user', 'subscription', 'started_at', 'Order__id']