from django.db import models
from .services import *

class Payment(models.Model):
    method = models.TextField(max_length=32)
    status = models.CharField(max_length=16)
    pay_time = models.DateTimeField(auto_created=False, null=True)
    created_time = models.DateTimeField(auto_created=True)
    cost = models.IntegerField()
    payment_id = models.CharField(max_length=128)
    discount = models.FloatField()

    class Meta:
        verbose_name = 'Платёж'  # Имя модели в единственном числе
        verbose_name_plural = 'Платежи'  # Имя модели во множественном числе


    @property
    def is_payment(self) -> bool: return True if self.status == "succesfull" else False

    @classmethod
    def create__payment(method_name, cost, request, products, discount):
        """Создание платежа"""

        method = get_method(method_name).create_payment(products, cost, discount, request)
        return Payment(
            method = method.name,
            status = "started",
            cost = cost,
            payment_id = method.id, 
            discount=discount
        ).save()

    def check__status(self): 
        """Проверка и обновление статуса платежа"""

        method_answer = get_method(self.method, self.payment_id).check_status()
        self.status = method_answer
        self.save()
        
        return method_answer

    def cancel_payment(self) -> bool: 
        """Отмена платежа с возвратом ДС"""

        return get_method(self.method, self.payment_id).cancel_payment()

