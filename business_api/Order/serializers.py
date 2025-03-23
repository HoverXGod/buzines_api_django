from rest_framework import serializers
from .models import Order, SalesChannel, OrderItem
from Payment.serializers import PaymentSerializer
from User.serializers import UserSerializer
from Product.serializers import ProductSerializer

class OrderSerializer(serializers.ModelSerializer): 

    user = UserSerializer
    payment = PaymentSerializer

    class Meta:
        model = Order
        depth = 1
        fields = ['id', 'payment', 'user', 'date', 'dilivery', 'dilivery_status', 'products',
                  'chanell', 'updated_at', 'status', 'shipping_address', 'billing_address', 'notes']

class SalesChanellSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesChannel
        field = ['id', 'name', 'description']

class OrderItemSerializer(serializers.ModelSerializer):

    order = OrderSerializer
    product = ProductSerializer

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'quantity', 'price', 'discount']