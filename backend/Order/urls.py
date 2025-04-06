from django.urls import path
from .views import *

urlpatterns = [
    path('api/order/get_all_orders', GetAllOrders.as_view()), 
    path('api/order/get_my_orders', GetMyOrders.as_view()), 
    path('api/order/get_order', GetOrder.as_view()), 
    path('api/order/get_user_orders', GetUserOrders.as_view()), 
    path('api/order/start_order', StartOrder.as_view()), 
]