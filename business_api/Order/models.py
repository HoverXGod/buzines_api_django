from django.db import models
from Payment.models import Payment
from User.models import User
from Product.models import Cart, Promotion, PersonalDiscount, Promocode

class Order(models.Model):
    """Модель заказа с привязкой к платежу"""


    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=False)
    products = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_created=True)
    dilivery = models.TextField(max_length=512)

    class Meta:
        verbose_name = 'Заказ'  # Имя модели в единственном числе
        verbose_name_plural = 'Заказы'  # Имя модели во множественном числе


    @classmethod
    def create__order(request, promo, method_name, dilivery:str=""): 
        """Создание заказа в поле products необходимо указать id товаров через запятую без пробелов, dilivery это статус доставки если она есть"""
        
        products = Cart.get_user_cart(request.user)

        user = request.user

        cost = Cart.calculate_base_cost(user=user)
        discount = cost - Cart.calculate_total(user=user, promo_code=promo)

        return Order(
            user = request.user,
            payment = Payment.create__payment(
                method_name,
                cost,
                request,
                products,
                discount
                ),
            products = products,
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
