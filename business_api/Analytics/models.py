# analytics/models.py
from django.db import models, transaction
from django.db.models import Index, F, Sum, Avg
from User.models import User
from Product.models import Product, Category
from Order.models import Order, OrderItem
from Payment.models import Payment
from .managers import *

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
    session_data = models.JSONField(default=dict, blank=True, null=True)
    device_type = models.CharField(max_length=20, choices=[
        ('mobile', 'Мобильный'),
        ('desktop', 'Десктоп'),
        ('tablet', 'Планшет')
    ], null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)  # Добавлено

    objects = SalesFunnelManager()

    class Meta:
        indexes = [
            models.Index(fields=['stage', 'timestamp']),
            models.Index(fields=['user', 'product'])
        ]
        verbose_name_plural = 'Воронки продаж'
        verbose_name = verbose_name_plural

    def get_product_performance(self):
        return ProductPerformance.objects.get(
            product=self.order_item.product,
            date=self.timestamp.date()
        )

    def __str__(self):
        return f"{self.user} - {self.stage}"
    
    def get_conversion_time(self, target_stage):
        """
        Получение времени конверсии до целевого этапа
        """
        target_entry = self.__class__.objects.filter(
            user=self.user,
            product=self.product,
            stage=target_stage,
            timestamp__gt=self.timestamp
        ).first()
        
        if target_entry:
            return target_entry.timestamp - self.timestamp
        return None

    def get_related_metrics(self):
        """
        Получение связанных метрик продукта
        """
        from .models import ProductPerformance
        return ProductPerformance.objects.filter(
            product=self.product,
            date=self.timestamp.date()
        ).first()

    def to_dict(self):
        """
        Сериализация в словарь
        """
        return {
            'id': self.id,
            'user_id': self.user.id if self.user else None,
            'product_id': self.product.id if self.product else None,
            'stage': self.stage,
            'timestamp': self.timestamp.isoformat(),
            'device_type': self.device_type,
            'session_data': self.session_data
        }

class CustomerLifetimeValue(models.Model):
    """Пожизненная ценность клиента (LTV)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_frequency = models.FloatField()
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    category_spend = models.DecimalField(max_digits=12, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    objects = CustomerLifetimeValueManager()

    def calculate_clv(self):
        return round(float(self.avg_order_value) * self.purchase_frequency * 12, 2)  # На год

    def __str__(self):
        return f"LTV {self.user}"
    
    class Meta:
        verbose_name_plural = 'Пожизненная ценность пользователей'
        verbose_name = verbose_name_plural

class ProductPerformance(models.Model):
    """Анализ эффективности товаров"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='analysis')
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
    discount_impact = models.DecimalField(max_digits=5, decimal_places=2)
    
    objects = PerformanceManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['avg_selling_price'])
        ]

        verbose_name_plural = 'Анализ продуктов'
        verbose_name = verbose_name_plural

    def update_metrics(self):
        """Метод оставлен для совместимости, вызывается из менеджера"""

        items = OrderItem.objects.filter(
            product=self.product
        ).aggregate(
            total_units=Sum('quanity'),
            avg_price=Avg('price'),
            total_discount=Sum('discount')
        )

        purchases = OrderItem.objects.filter(
            product=self.product,
        ).values('order')

        values = [item['order'] for item in purchases]

        count = 0
        for item in Order.objects.filter(id__in=values):
            if item.payment.is_payment:
                count += 1
        
        self.metrics['purchases'] = count
        self.total_units_sold = items['total_units'] or 0
        self.avg_selling_price = items['avg_price'] or Decimal('0.00')
        self.discount_impact = items['total_discount'] or Decimal('0.00')
        self.metrics['stock_level'] = self.product.stock

    def add_view(self):
        self.metrics['views'] = self.metrics['views'] + 1
        self.save()

    def add_cart(self):
        self.metrics['cart_adds'] + self.metrics['cart_adds'] + 1
        self.save()

    def update_conversion_rate(self):
        """Обновление коэффициента конверсии"""
        self.metrics['conversion_rate'] = PerformanceManager._calculate_conversion_rate(
            self.metrics.get('purchases', 0),
            self.metrics.get('views', 1)
        )



    def __str__(self):
        return f"{self.product} - {self.date}"

class CohortAnalysis(models.Model):
    """Автоматический когортный анализ"""
    cohort_date = models.DateField(help_text="Дата формирования когорты")
    retention_day = models.PositiveIntegerField(help_text="День удержания")
    primary_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Автоматически определяемая категория"
    )
    
    metrics = models.JSONField(default=dict, help_text="""
    {
        'total_users': int,
        'active_users': int,
        'revenue': float,
        'avg_order_value': float,
        'orders_count': int,
        'arppu': float
    }""")

    objects = CohortAnalysisManager()

    class Meta:
        unique_together = ('cohort_date', 'retention_day', 'primary_category')
        indexes = [
            models.Index(fields=['cohort_date', 'primary_category']),
            models.Index(fields=['retention_day'])
        ]
        ordering = ['-cohort_date', 'retention_day']

        verbose_name_plural = 'Когортный анализ'
        verbose_name = verbose_name_plural

    def __str__(self):
        return f"Cohort {self.cohort_date} - Day {self.retention_day}"

    @property
    def retention_rate(self):
        """Уровень удержания в процентах"""
        if self.metrics.get('total_users', 0) > 0:
            return round((self.metrics['active_users'] / self.metrics['total_users']) * 100, 2)
        return 0.0
    
    def refresh_metrics(self):
        with transaction.atomic():
            self.delete()
            new_entry = CohortAnalysis.objects.add_entry()
            return new_entry
    
class PaymentAnalysis(models.Model):
    """Детальный анализ платежей"""
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    gateway_performance = models.FloatField(
        null=True,
        help_text="Время обработки в секундах"
    )
    fraud_indicators = models.JSONField(
        default=dict,
        help_text="Флаги рисков мошенничества"
    )
    risk_score = models.FloatField(
        null=True,
        help_text="Общая оценка риска (0-100)"
    )
    chargeback_probability = models.FloatField(
        null=True,
        help_text="Вероятность возврата платежа (%)"
    )
    analysis_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Время проведения анализа"
    )

    analysis_date = models.DateField(auto_now=True)

    objects = PaymentAnalysisManager()

    class Meta:
        indexes = [
            models.Index(fields=['risk_score']),
            models.Index(fields=['payment']),
            models.Index(fields=['analysis_timestamp'])
        ]
        verbose_name = 'Анализ платежа'
        verbose_name_plural = 'Анализы платежей'

    def __str__(self):
        return f"Анализ #{self.payment.payment_id}"

    @property
    def risk_category(self):
        """Категоризация риска с градациями"""
        if self.risk_score < 25:
            return "Низкий"
        elif self.risk_score < 50:
            return "Умеренный"
        elif self.risk_score < 75:
            return "Высокий"
        return "Критический"

    def refresh_analysis(self):
        """Обновление анализа"""
        self.delete()
        return self.objects.add_entry(self.payment)

class OrderAnalytics(models.Model):
    """Расширенная аналитика заказов"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    time_performance = models.FloatField(default=1, help_text="Время обработки в секундах")
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