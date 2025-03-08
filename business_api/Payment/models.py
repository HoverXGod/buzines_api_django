from django.db import models

class Payment(models.model):
    method = models.TextField(max_length=32)
    status = models.CharField(max_length=16)
    pay_time = models.DateTimeField(auto_created=False)
    created_time = models.DateTimeField(auto_created=True)
    cost = models.IntegerField(max_length=16)
    payment_id = models.CharField(max_length=128)

    @property
    def is_payment(self) -> bool: return

    @classmethod
    def create__payment(): pass

    def check__status(self): pass

    def delete(self): pass

