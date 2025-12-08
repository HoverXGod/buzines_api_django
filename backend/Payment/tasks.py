from Payment.models import Payment
from business_api.celery import app
from datetime import datetime
from Payment.services import get_method
from Order.models import Order
from django.db import transaction

@app.task(bind=True)
def check_payment_status(self, cls: type[str], db_name: type[str]) -> None:
    with transaction.atomic(using=db_name):
        cls = Payment.objects.get(payment_id=cls)

        method_answer = get_method(cls.method, cls.payment_id).check_status()
        cls.status = method_answer
        cls.save()

        if cls.is_payment:
            cls.pay_time = datetime.now()
            cls.save()

            from Product.models import UserSubscriptionItem
            UserSubscriptionItem.check_all_user_subscriptions(cls.user)

            from Analytics.models import PaymentAnalysis
            PaymentAnalysis.objects.add_entry(cls, db_name)

            cls.order.first().update_status(method_answer)

        else:
            self.request.retries += 1
            raise self.retry(countdown=15)

    return method_answer
