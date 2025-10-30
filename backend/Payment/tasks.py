from .models import Payment
from processors import background
from time import timezone
from .services import get_method
from Order.models import Order

@background.task()
def check_payment_status(cls: type[str]) -> None:

    from Payment.models import Payment

    cls = Payment.objects.get(payment_id=cls)

    method_answer = get_method(cls.method, cls.payment_id).check_status()
    cls.status = method_answer
    cls.save()

    if cls.is_payment:
        cls.pay_time = timezone.now()
        cls.save()

        from Product.models import UserSubscriptionItem
        UserSubscriptionItem.check_all_user_subscriptions(cls.user)

        from Analytics.models import PaymentAnalysis
        PaymentAnalysis.objects.add_entry(cls)

        cls.order.update_status(method_answer)

    else: raise ZeroDivisionError
