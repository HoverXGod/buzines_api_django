from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer): 

    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'status', 'created_time', 'cost', 'pay_time']