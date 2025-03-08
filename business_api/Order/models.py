from django.db import models
from Payment.models import Payment
from User.models import User

class Order(models.model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=False)
    products = models.models.ManyToManyField("Product.Product", verbose_name=("Продукты"))
    date = models.DateTimeField(auto_created=True)
    dilivery = models.TextField(max_length=512)

    @classmethod
    def create__order(): pass

    def get_payment(self): return self.payment

    


