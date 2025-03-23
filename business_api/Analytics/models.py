# analytics/models.py
from django.db import models
from django.db.models import Index, F, Sum, Avg
from User.models import User
from Product.models import Product, Category
from Order.models import Order, Payment, OrderItem

class SalesFunnel(models.Model):
    """Воронка продаж с детализацией по этапам"""
    STAGE_CHOICES = [
        ('view', 'Просмотр'),
        ('cart', 'Корзина'),
        ('checkout', 'Оформление'),
        ('payment', 'Оплата'),
        ('delivery', 'Доставка')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_data = models.JSONField(default=dict)
    device_type = models.CharField(max_length=20, choices=[
        ('mobile', 'Мобильный'),
        ('desktop', 'Десктоп'),
        ('tablet', 'Планшет')
    ])
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True)  # Добавлено

    class Meta:
        indexes = [
            models.Index(fields=['stage', 'timestamp']),
            models.Index(fields=['user', 'product'])
        ]

    def get_product_performance(self):
        return ProductPerformance.objects.get(
            product=self.order_item.product,
            date=self.timestamp.date()
        )

    def __str__(self):
        return f"{self.user} - {self.stage}"

class CustomerLifetimeValue(models.Model):
    """Пожизненная ценность клиента (LTV)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_frequency = models.FloatField()
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    category_spend = models.DecimalField(max_digits=12, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_clv(self):
        return self.avg_order_value * self.purchase_frequency * 12  # На год

    def __str__(self):
        return f"LTV {self.user}"

class ProductPerformance(models.Model):
    """Анализ эффективности товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    
    metrics = models.JSONField(default=dict, help_text="""{
        'views': 0,
        'cart_adds': 0,
        'purchases': 0,
        'conversion_rate': 0.0,
        'stock_level': 0
    }""")
    total_units_sold = models.PositiveIntegerField(default=0)
    avg_selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_impact = models.DecimalField(max_digits=5, decimal_places=2)  # Влияние скидок
    
    class Meta:
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['avg_selling_price'])
        ]

    def update_metrics(self):
        # Агрегация данных из OrderItem
        items = OrderItem.objects.filter(
            product=self.product,
            order__created_at__date=self.date
        ).aggregate(
            total_units=Sum('quantity'),
            avg_price=Avg('price_at_purchase'),
            total_discount=Sum('applied_discount')
        )
        
        self.total_units_sold = items['total_units'] or 0
        self.avg_selling_price = items['avg_price'] or 0
        self.discount_impact = items['total_discount'] or 0
        self.save()

    def update_conversion_rate(self):
        total_views = self.metrics.get('views', 1)
        self.metrics['conversion_rate'] = round(
            self.metrics.get('purchases', 0) / total_views * 100, 2
        )
        self.save()

    def __str__(self):
        return f"{self.product} - {self.date}"

class CohortAnalysis(models.Model):
    """Когортный анализ с привязкой к категориям"""
    cohort_date = models.DateField()
    retention_day = models.PositiveIntegerField()
    primary_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    metrics = models.JSONField(default=dict, help_text="""{
        'total_users': 0,
        'active_users': 0,
        'revenue': 0.0,
        'avg_order_value': 0.0
    }""")

    class Meta:
        unique_together = ('cohort_date', 'retention_day', 'primary_category')
        indexes = [
            models.Index(fields=['cohort_date', 'primary_category']),
            models.Index(fields=['retention_day'])
        ]

    def __str__(self):
        return f"Cohort {self.cohort_date} - Day {self.retention_day}"

class PaymentAnalysis(models.Model):
    """Детальный анализ платежей"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    gateway_performance = models.FloatField(help_text="Время обработки в секундах")
    fraud_indicators = models.JSONField(default=dict)
    risk_score = models.FloatField(null=True)
    chargeback_probability = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['risk_score']),
        ]

    def __str__(self):
        return f"Анализ платежа #{self.payment.id}"

class OrderAnalytics(models.Model):
    """Расширенная аналитика заказов"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    margin = models.DecimalField(max_digits=12, decimal_places=2)
    acquisition_source = models.CharField(max_length=100)
    customer_journey = models.JSONField(default=dict)
    predicted_churn_risk = models.FloatField(null=True)
    item_metrics = models.JSONField(default=dict, help_text="""
    {
        "top_items": [{"id": 1, "name": "Товар", "units": 5}],
        "basket_diversity": 0.75  # Индекс разнообразия корзины
    }
    """)

    def analyze_items(self):
        items = OrderItem.objects.filter(order=self.order)
        
        # Топ товаров
        top_items = items.values('product__name').annotate(
            total_units=Sum('quantity')
        ).order_by('-total_units')[:5]
        
        # Индекс разнообразия
        unique_products = items.values('product').distinct().count()
        self.item_metrics = {
            'top_items': list(top_items),
            'basket_diversity': unique_products / items.count() if items.count() > 0 else 0
        }
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['margin']),
        ]

    def calculate_margin(self):
        return self.order.total_price - sum(
            item.product.cost_price * item.quantity 
            for item in self.order.items.all()
        )

    def __str__(self):
        return f"Анализ заказа #{self.order.id}"

class InventoryTurnover(models.Model):
    """Оборачиваемость запасов"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    
    stock_turnover = models.FloatField()
    stockout_days = models.PositiveIntegerField()
    demand_forecast = models.PositiveIntegerField()

    class Meta:
        unique_together = ('product', 'period_start')
        indexes = [
            models.Index(fields=['category', 'period_start']),
        ]

    def __str__(self):
        return f"Оборачиваемость {self.product}"

class CustomerBehavior(models.Model):
    """Поведенческая аналитика клиентов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_metrics = models.JSONField(default=dict, help_text="""{
        'page_views': 0,
        'time_spent': 0,
        'cart_actions': 0
    }""")
    preference_profile = models.JSONField(default=dict)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'last_activity']),
            models.Index(fields=['preference_profile'])
        ]

    def update_engagement_score(self):
        score = (
            self.session_metrics.get('page_views', 0) * 0.3 +
            self.session_metrics.get('cart_actions', 0) * 0.7
        )
        self.preference_profile['engagement_score'] = score
        self.save()

    def __str__(self):
        return f"Поведение {self.user}"

class OrderItemAnalytics(models.Model):
    """Глубокая аналитика по позициям заказов"""
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE)
    margin = models.DecimalField(max_digits=10, decimal_places=2)
    profitability_index = models.FloatField()  # Индекс рентабельности
    cross_sell_products = models.ManyToManyField(Product)  # Сопутствующие товары
    
    class Meta:
        indexes = [
            models.Index(fields=['margin']),
        ]

    def calculate_margin(self):
        return self.order_item.price_at_purchase - self.order_item.product.cost_price