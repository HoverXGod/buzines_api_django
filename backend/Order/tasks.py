from business_api.celery import app
from datetime import datetime
from django.apps import apps
from .models import Order
from django.db import transaction

@app.task(bind=True)
def create_order_task(self, db_name: type[str]):
    with transaction.atomic(using=db_name):
        order = Order.create__order(user_id, promo, method_name)

    return order