from business_api.celery import app
from datetime import datetime
from django.apps import apps
from .models import Order

@app.task(bind=True)
def create_order_task(self):
    order = Order.create__order(user_id, promo, method_name)
    return order