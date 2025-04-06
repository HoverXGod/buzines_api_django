from django.urls import path
from .views import *

urlpatterns = [
    path('api/payment/cancel_payment', CancelPayment.as_view()), 
    path('api/payment/check_status', CheckStatus.as_view()), 
]