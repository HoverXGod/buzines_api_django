from rest_framework import serializers
from .models import Order
from Payment.serializers import PaymentSerializer
from User.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer): 

    user = UserSerializer
    payment = PaymentSerializer

    class Meta:
        model = Order
        fields = ['id', 'payment', 'user', 'date', 'dilivery', 'products']