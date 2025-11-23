from celery import shared_task
from datetime import datetime
from django.apps import apps
from .models import Order

@shared_task(bind=True, name="create_order")
def create_order_task(self):
    order = Order.create__order(user_id, promo, method_name)
    return order