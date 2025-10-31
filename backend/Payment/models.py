from django.db import models
from User.models import User
from django.utils import timezone
from .services import *

class Payment(models.Model):

    PAYMENT_STATUS = (
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')
    method = models.TextField(max_length=32)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    pay_time = models.DateTimeField(auto_created=False, null=True)
    created_time = models.DateTimeField(auto_now=True, editable=False)
    processed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    payment_id = models.CharField(max_length=128)
    discount = models.FloatField()
    needs_review = models.BooleanField(default=False)
    payment_gateway = models.CharField(max_length=30)  # Платежный шлюз
    fee = models.DecimalField(max_digits=10, decimal_places=2)  # Комиссия
    currency = models.CharField(max_length=3, default="RUB")  # Валюта платежа
    chargeback_status = models.BooleanField(default=False)  # Возврат средств
    risk_score = models.FloatField(null=True)  # Оценка риска (антифрод)
    
    @property
    def amount(self): return self.cost

    @property
    def payment_gateway(self) -> object: return self.method

    def __str__(self):
        return f"{self.payment_id} | статус {self.status}"

    class Meta:
        verbose_name = 'Платёж'  # Имя модели в единственном числе
        verbose_name_plural = 'Платежи'  # Имя модели во множественном числе

    @property
    def is_payment(self) -> bool: return True if self.status == "completed" else False

    @staticmethod
    def create__payment(method_name, cost, request, products, discount, user):
        """Создание платежа"""

        method = get_method(method_name)
        method.create_payment(products, cost, discount, request)
        
        this_payment = Payment(
            user = user,
            method = method.name,
            cost = cost,
            payment_id = method.id, 
            discount=discount,
            fee = 0
        )

        this_payment.save()

        return this_payment

    def check__status(self): 
        """Проверка и обновление статуса платежа"""

        method_answer = get_method(self.method, self.payment_id).check_status()
        self.status = method_answer
        self.save()

        if self.is_payment:
            self.pay_time = timezone.now()
            self.save()

            from Product.models import UserSubscriptionItem
            UserSubscriptionItem.check_all_user_subscriptions(self.user)

            from Analytics.models import PaymentAnalysis
            PaymentAnalysis.objects.add_entry(self)
        else: raise ZeroDivisionError

        return method_answer

    def cancel_payment(self) -> bool: 
        """Отмена платежа с возвратом ДС"""

        return get_method(self.method, self.payment_id).cancel_payment()

