from Payment.models import Payment
from celery import shared_task
from datetime import datetime
from Payment.services import get_method
from Order.models import Order

@shared_task(bind=True, name='Payment.tasks.check_payment_status')
def check_payment_status(self, cls: type[str]) -> None:

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
        PaymentAnalysis.objects.add_entry(cls)

        cls.order.first().update_status(method_answer)

    else:
        self.request.retries += 1
        raise self.retry(countdown=15)

    return method_answer
