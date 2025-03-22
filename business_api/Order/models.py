from django.db import models
from Payment.models import Payment
from User.models import User
from Product.models import Cart, Promotion, PersonalDiscount, Promocode

class Order(models.Model):
    """Модель заказа с привязкой к платежу"""


    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=False)
    products = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_now=True)
    dilivery = models.TextField(max_length=512)
    dilivery_status = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'Заказ'  # Имя модели в единственном числе
        verbose_name_plural = 'Заказы'  # Имя модели во множественном числе


    @staticmethod
    def create__order(request, promo, method_name): 
        """Создание заказа, dilivery это статус доставки если она есть"""
        
        products = Cart.get_user_cart(request.user)

        user = request.user

        dilivery = ""

        cost = Cart.calculate_base_cost(user=user)
        discount = cost - Cart.calculate_total(user=user, promo_code=promo)

        Order.objects.create(
            user = user,
            payment = Payment.create__payment(
                method_name,
                cost,
                request,
                products,
                discount
                ),
            products = Cart.get_user_cart_id(user=user).split(','),
            dilivery = dilivery
        )

        Cart.delete_user_cart(user)

        return Order.objects.last()
    
    def cancel_order(self, method_name) -> bool: 
        """Возврат средств, возвращат успешность выполнения функции"""

        answer = self.payment.cancel_payment(method_name)
        self.delete()
        
        return answer
    
    def update_status(self, method_name) -> str:
        """Возвращает и обновляет статус платежа"""

        return self.payment.check__status(method_name)
