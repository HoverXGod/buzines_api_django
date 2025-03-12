from django.db import models
from .services import *

class Payment(models.model):
    method = models.TextField(max_length=32)
    status = models.CharField(max_length=16)
    pay_time = models.DateTimeField(auto_created=False, null=True)
    created_time = models.DateTimeField(auto_created=True)
    cost = models.IntegerField(max_length=16)
    payment_id = models.CharField(max_length=128)

    @property
    def is_payment(self) -> bool: return True if self.status == "succesful" else False

    @classmethod
    def create__payment(method_name, cost, request, products):
        """Создание платежа"""

        method = get_method(method_name).create_payment(products, cost, request)
        return Payment(
            method = method.name,
            status = "started",
            cost = cost,
            payment_id = method.id
        ).save()

    def check__status(self, method_name): 
        """Проверка и обновление статуса платежа"""

        method_answer = get_method(method_name, self.payment_id).check_status()
        self.status = method_answer
        self.save()
        
        return method_answer

    def cancel_payment(self, method_name) -> bool: 
        """Отмена платежа с возвратом ДС"""

        return get_method(method_name, self.payment_id).cancel_payment()

