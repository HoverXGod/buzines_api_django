from django.db import models
from Payment.models import Payment
from User.models import User
from Product.models import Cart, Product
from Analytics.utils import process_order_item

class SalesChannel(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=512)

    class Meta:
        verbose_name = 'Канал продаж'  # Имя модели в единственном числе
        verbose_name_plural = 'Каналы продаж'  # Имя модели во множественном числе

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def check_base_chanell():
        try: chanell = SalesChannel.objects.get(id = 1)
        except: return SalesChannel.objects.create(
            name="online",
            description="""Канал онлайн продаж. Продажы происходят из интернет магазина""")
        
        if chanell.name != "online": 
            chanell.name = "online"
            chanell.save()


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
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, related_name='payment')
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

    @property
    def total(self): return self.payment.cost


    @staticmethod
    def create__order(request, promo, method_name): 
        """Создание заказа, dilivery это статус доставки если она есть"""
        
        products = Cart.get_user_cart(request.user)

        user = request.user

        data = Cart.calculate_total(user=user, promo_code=promo)

        price_with_discount = data[0]
        product_dict = data[1]

        cost = Cart.calculate_base_cost(user=user)
        discount = cost - price_with_discount

        Order.objects.create(
            user = user,
            payment = Payment.create__payment(
                method_name,
                cost,
                request,
                products,
                discount,
                user
                ),
            products = Cart.get_user_cart_id(user=user).split(','),
            delivery = "",
            chanell = SalesChannel.objects.get(id=1)
        )

        order = Order.objects.last()

        for item in product_dict:
            order_item = OrderItem.objects.create(
                order = order,
                product = product_dict[item]['product'],
                quanity = product_dict[item]['quanity'],
                price = product_dict[item]['price'],
                discount = product_dict[item]['discount'],
                promotion_name = product_dict[item]['promotion'].name,
                promotion_type = product_dict[item]['promotion'].__class__
            )
            process_order_item(order_item)

        from Analytics.models import SalesFunnel, CustomerLifetimeValue

        try:
            CustomerLifetimeValue.objects.create_clv(user = user)
        except: pass

        for item in order.items.all():

            try:
                SalesFunnel.objects.add_entry(
                    user=request.user,
                    product=item.product,
                    stage='checkout',
                    session_data={}
                    )
            except :pass
            
        from django.core.management import call_command
        call_command('init_cohort')

        Cart.delete_user_cart(user)

        return order
    
    def cancel_order(self) -> bool: 
        """Возврат средств, возвращат успешность выполнения функции"""

        answer = self.payment.cancel_payment()
        self.delete()
        
        return answer
    
    def update_status(self) -> str:
        """Возвращает и обновляет статус платежа"""

        status = self.payment.check__status()
    
        
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

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quanity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    promotion_name = models.CharField(max_length=32)
    promotion_type = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.product.name} * {self.quanity}"
    
    @property
    def date(self):
        return self.order.date

    class Meta:
        indexes = [
            models.Index(fields=['product', 'discount'])
        ]
        verbose_name = 'Товар в заказе'  # Имя модели в единственном числе
        verbose_name_plural = 'Товары в заказах'  # Имя модели во множественном числе
