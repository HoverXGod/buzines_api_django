from django.db import models
from Payment.models import Payment
from User.models import User
from django.utils.functional import cached_property

class SalesChannel(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=512)

    class Meta:
        verbose_name = 'Канал продаж'  # Имя модели в единственном числе
        verbose_name_plural = 'Каналы продаж'  # Имя модели во множественном числе

    def __str__(self):
        return f"{self.name}"

class Order(models.Model):
    """Модель заказа с привязкой к платежу"""

    ORDER_STATUS = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, related_name='order')
    products = models.TextField(max_length=1024)
    chanell = models.ForeignKey(SalesChannel, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='new')
    delivery = models.TextField(max_length=512)
    delivery_status = models.CharField(max_length=32)
    shipping_address = models.TextField(default="")
    billing_address = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['-date', 'status']),
        ]
        verbose_name = 'Заказ'  # Имя модели в единственном числе
        verbose_name_plural = 'Заказы'  # Имя модели во множественном числе

    def __str__(self): 
        return f"id:{self.id}"

    @cached_property
    @property
    def total(self): return self.payment.cost

    @staticmethod
    def create__order(user_id, promo, method_name):
        """Создание заказа, dilivery это статус доставки если она есть"""

        from Product.models import Cart

        products = Cart.get_user_cart(user_id=user_id)

        user = User.objects.get(id=user_id)

        data = Cart.calculate_total(user_id=user.id, promo_code=promo)

        price_with_discount = data[0]
        product_dict = data[1]

        cost = Cart.calculate_base_cost(user_id=user.id)
        discount = cost - price_with_discount

        payment = Payment.create__payment(
                method_name,
                cost,
                products,
                discount,
                user
                )

        Order.objects.create(
            user = user,
            payment = payment,
            products = Cart.get_user_cart_id(user_id=user.id).split(','),
            delivery = "",
            chanell = SalesChannel.objects.get(id=1)
        )

        order = Order.objects.last()

        from context.Order.order_create import order_create

        order_create(
            request=request,
            order=order,
            product_dict=product_dict
        )

        for key in product_dict:
            product = product_dict[key]['product']
            try:
                UserSubscriptionItem.create(
                    order=order,
                    user=user,
                    subscription=product.subscription,
                )
            except: pass

        Cart.delete_user_cart(user)

        from Payment.tasks import check_payment_status
        check_payment_status.delay(payment.payment_id)

        return order

    def cancel_order(self) -> bool:
        """Возврат средств, возвращат успешность выполнения функции"""

        answer = self.payment.cancel_payment()
        self.delete()
        
        return answer
    
    def update_status(self, status) -> str:
        """Возвращает и обновляет статус платежа"""
    
        
        from Analytics.models import SalesFunnel

        if self.payment.is_payment:
            for item in self.items.all():
                try:
                    SalesFunnel.objects.add_entry(
                        user=self.user,
                        product=item.product,
                        stage='payment',
                        session_data={}
                        )
                except: pass

        return status

class OrderItem(models.Model):
    from Product.models import Product
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quanity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    promotion_name = models.CharField(max_length=32)
    promotion_type = models.CharField(max_length=32)

    def __str__(self):
        return f" {self.product.name} * {self.quanity}"

    @cached_property
    @property
    def date(self):
        return self.order.date

    class Meta:
        indexes = [
            models.Index(fields=['product', 'discount'])
        ]
        verbose_name = 'Товар в заказе'  # Имя модели в единственном числе
        verbose_name_plural = 'Товары в заказах'  # Имя модели во множественном числе
