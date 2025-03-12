from django.db import models
from Payment.models import Payment
from User.models import User

class Order(models.model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=False)
    products = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_created=True)
    dilivery = models.TextField(max_length=512)

    @classmethod
    def create__order(request, method_name, cost,dilivery:str="", products:str=""): 
        """Создание заказа в поле products необходимо указать id товаров через запятую без пробелов, dilivery это статус доставки если она есть"""
        
        return Order(
            user = request.user,
            payment = Payment.create__payment(
                method_name,
                cost,
                request,
                products
                ),
            products = None,
            dilivery = dilivery
        ).save()
    
    def cancel_order(self, method_name) -> bool: 
        """Возврат средств, возвращат успешность выполнения функции"""

        answer = self.payment.cancel_payment(method_name)
        self.delete()
        
        return answer
    
    def update_status(self, method_name) -> str:
        """Возвращает и обновляет статус платежа"""

        return self.payment.check__status(method_name)
