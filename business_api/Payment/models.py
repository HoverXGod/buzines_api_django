from django.db import models
from .services import *

class Payment(models.Model):

    PAYMENT_STATUS = (
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    )

    method = models.TextField(max_length=32)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    pay_time = models.DateTimeField(auto_created=False, null=True)
    created_time = models.DateTimeField(auto_now=True, editable=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    payment_id = models.CharField(max_length=128)
    discount = models.FloatField()

    # Новые поля для аналитики
    payment_gateway = models.CharField(max_length=30)  # Платежный шлюз
    fee = models.DecimalField(max_digits=10, decimal_places=2)  # Комиссия
    currency = models.CharField(max_length=3, default="RUB")  # Валюта платежа
    chargeback_status = models.BooleanField(default=False)  # Возврат средств
    risk_score = models.FloatField(null=True)  # Оценка риска (антифрод)
    
    @property
    def amount(self): return self.cost

    @property
    def payment_gateway(self): return self.method

    def __str__(self):
        return f"{self.payment_id} | статус {self.status}"

    class Meta:
        verbose_name = 'Платёж'  # Имя модели в единственном числе
        verbose_name_plural = 'Платежи'  # Имя модели во множественном числе

    @property
    def is_payment(self) -> bool: return True if self.status == "succesfull" else False

    @staticmethod
    def create__payment(method_name, cost, request, products, discount):
        """Создание платежа"""

        method = get_method(method_name)
        method.create_payment(products, cost, discount, request)
        
        Payment.objects.create(
            method = method.name,
            cost = cost,
            payment_id = method.id, 
            discount=discount,
            fee = 0
        )

        return Payment.objects.last()

    def check__status(self): 
        """Проверка и обновление статуса платежа"""

        method_answer = get_method(self.method, self.payment_id).check_status()
        self.status = method_answer
        self.save()
        
        return method_answer

    def cancel_payment(self) -> bool: 
        """Отмена платежа с возвратом ДС"""

        return get_method(self.method, self.payment_id).cancel_payment()

