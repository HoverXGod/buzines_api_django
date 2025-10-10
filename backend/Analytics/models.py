# analytics/models.py
from django.db import models, transaction
from django.db.models import Index, F, Sum, Avg
from User.models import User
from Product.models import Product, Category
from Order.models import Order, OrderItem
from Payment.models import Payment
from .managers import *
from datetime import datetime

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
    avg_selling_price = models.DecimalField(max_digits=20, decimal_places=2)
    discount_impact = models.DecimalField(max_digits=20, decimal_places=2)
    
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
        self.discount_impact = Decimal(items['total_discount']) or Decimal('0.00')
        self.metrics['stock_level'] = self.product.stock

    def add_view(self):
        self.metrics['views'] = self.metrics['views'] + 1
        self.save()

    def add_cart(self):
        self.metrics['cart_adds'] = self.metrics['cart_adds'] + 1
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
    """Расширенная аналитика заказов с автоматическим расчетом"""
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    margin = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Маржинальность заказа"
    )
    acquisition_source = models.CharField(
        max_length=100,
        help_text="Источник привлечения клиента"
    )
    customer_journey = models.JSONField(
        default=dict,
        help_text="Данные о пути клиента"
    )
    predicted_churn_risk = models.FloatField(
        null=True,
        help_text="Прогнозируемый риск оттока (%)"
    )
    item_metrics = models.JSONField(
        default=dict,
        help_text="Метрики товарной корзины"
    )

    objects = OrderAnalyticsManager()

    class Meta:
        indexes = [
            models.Index(fields=['margin']),
            models.Index(fields=['acquisition_source']),
            models.Index(fields=['predicted_churn_risk'])
        ]
        verbose_name = 'Анализ заказа'
        verbose_name_plural = 'Аналитика заказов'

    def __str__(self):
        return f"Анализ #{self.order.id}"

    @property
    def margin_percentage(self):
        """Маржинальность в процентах"""
        if self.order.payment.amount > 0:
            return (self.margin / self.order.payment.amount) * 100
        return 0.0

class InventoryTurnover(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    stock_turnover = models.FloatField()
    stockout_days = models.PositiveIntegerField()
    demand_forecast = models.PositiveIntegerField()

    objects = InventoryTurnoverManager()

    class Meta:
        unique_together = ('product', 'period_start')
        indexes = [
            models.Index(fields=['category', 'period_start']),
        ]
        verbose_name = 'Анализ оборачиваемости'
        verbose_name_plural = 'Аналитика оборачиваемости'

    def __str__(self):
        return f"Оборачиваемость {self.product}"
    
    def update_entry(self): 
        today = datetime.now().date()
        period_start = today.replace(day=1)

        product = self.product
        
        # Рассчитываем конец периода
        if period_start.month == 12:
            next_month = period_start.replace(year=period_start.year+1, month=1)
        else:
            next_month = period_start.replace(month=period_start.month+1)
        period_end = next_month - timedelta(days=1)

        # Получаем общее количество продаж за период
        total_sold = (
            product.orders.filter(
                order__date__gte=period_start,
                order__date__lte=period_end
            ).aggregate(total=Sum('quanity'))['total'] or 0
        )

        # Рассчитываем дни отсутствия товара
        stockout_days = self.calculate_stockout_days(product, period_start, period_end)

        # Расчет оборачиваемости
        avg_stock = self.calculate_avg_stock(product, period_start, period_end)
        stock_turnover = total_sold / avg_stock if avg_stock > 0 else 0

        period_end.__str__()

        time1, time2 = period_start.__str__(), period_end.__str__()

        self.period_start=time1
        self.period_end=time2
        self.stock_turnover=round(stock_turnover, 2)
        self.stockout_days=stockout_days
        self.demand_forecast=total_sold

        self.save()

    @staticmethod
    def calculate_avg_stock(product, start, end):
        # Получаем историю изменений запасов за период
        history = StockHistory.history.filter(
            product=product,
            date__gte=start,
            date__lte=end
        ).order_by('date')

        if not history.exists():
            return product.stock

        # Расчет среднего запаса по формуле среднего взвешенного
        total_days = (end - start).days + 1
        stock_days = []
        prev_stock = history.first().previous_stock
        prev_date = start

        for entry in history:
            days = (entry.date - prev_date).days
            stock_days.append(prev_stock * days)
            prev_date = entry.date
            prev_stock = entry.new_stock

        # Добавляем остаток дней после последней записи
        days_left = (end - prev_date).days + 1
        stock_days.append(prev_stock * days_left)

        return sum(stock_days) / total_days

    @staticmethod
    def calculate_stockout_days(product, start, end):
        # Получаем все изменения запасов за период
        history = StockHistory.history.filter(
            product=product,
            date__gte=start,
            date__lte=end
        ).order_by('date')

        if not history.exists():
            return 0 if product.stock > 0 else (end - start).days + 1

        stockout_days = 0
        current_stock = history.first().previous_stock
        current_date = start

        for entry in history:
            if current_stock == 0:
                stockout_days += (entry.date - current_date).days
            
            current_date = entry.date
            current_stock = entry.new_stock

        # Проверяем последний период
        if current_stock == 0:
            stockout_days += (end - current_date).days + 1

        return stockout_days


class CustomerBehavior(models.Model):
    """Поведенческая аналитика клиентов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_metrics = models.JSONField(default=dict,
        help_text="""{
        'page_views': 0,
        'time_spent': 0,
        'cart_actions': 0
    }""")
    preference_profile = models.JSONField(default=dict)
    last_activity = models.DateTimeField(auto_now=True)

    class CustomerBehaviorManager(models.Manager):
        def create(self, user):
            # Создаем объект через стандартный менеджер
            instance = super().create(user=user, session_metrics={
                'page_views': 0,
                'time_spent': 0,
                'cart_actions': 0
                })
            # Обновляем engagement_score (вызовет сохранение)
            instance.update_engagement_score()
            return instance

    objects = CustomerBehaviorManager()

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
    
    def add_view(self): 
        self.session_metrics['page_views'] = self.session_metrics['page_views'] + 1

    def cart_action(self): 
        self.session_metrics['cart_actions'] = self.session_metrics['cart_actions'] + 1

class OrderItemAnalytics(models.Model):
    """Расширенная аналитика по позициям заказов"""
    order_item = models.OneToOneField(
        OrderItem, 
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    margin = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Маржа"
    )
    profitability_index = models.FloatField(
        verbose_name="Индекс рентабельности (%)"
    )
    cross_sell_products = models.ManyToManyField(
        Product,
        verbose_name="Сопутствующие товары"
    )
    delivery_time = models.PositiveSmallIntegerField(
        verbose_name="Срок доставки (дни)",
        default=0
    )
    popularity_score = models.FloatField(
        verbose_name="Индекс популярности",
        default=0.0
    )
    return_rate = models.FloatField(
        verbose_name="Процент возвратов",
        default=0.0
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее обновление"
    )

    objects = OrderItemAnalyticsManager()

    class Meta:
        indexes = [
            models.Index(fields=['margin']),
            models.Index(fields=['delivery_time']),
            models.Index(fields=['popularity_score']),
        ]
        verbose_name = "Аналитика позиции заказа"
        verbose_name_plural = "Аналитика позиций заказов"

    def update_popularity(self):
        """Обновляет индекс популярности на основе продаж"""
        total_sold = self.order_item.product.order_items.count()
        recent_sold = self.order_item.product.order_items.filter(
            order__order_date__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        self.popularity_score = (recent_sold * 0.7) + (total_sold * 0.3)
        self.save(update_fields=['popularity_score'])

    def update_return_rate(self):
        """Рассчитывает процент возвратов для товара"""
        total_sold = self.order_item.product.order_items.count()
        returned = self.order_item.product.returns.count()
        
        self.return_rate = (returned / total_sold * 100) if total_sold > 0 else 0
        self.save(update_fields=['return_rate'])

    def __str__(self):
        return f"Аналитика для {self.order_item}"
    
class StockHistory(models.Model):
    class ChangeType(models.TextChoices):
        SALE = 'sale', 'Продажа'
        RESTOCK = 'restock', 'Пополнение'
        ADJUSTMENT = 'adjustment', 'Корректировка'

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    quantity = models.PositiveIntegerField()

    objects = models.Manager()  # Базовый менеджер

    class Meta:
        verbose_name = 'История запасов'
        verbose_name_plural = 'Истории запасов'

    class StockHistoryManager(models.Manager):
        def add_entry(self, product, quantity, change_type):
            previous_stock = product.stock
            
            if change_type == self.model.ChangeType.SALE:
                new_stock = previous_stock - quantity
            elif change_type == self.model.ChangeType.RESTOCK:
                new_stock = previous_stock + quantity
            else:
                new_stock = previous_stock  # Для корректировок нужно отдельное управление

            product.stock = new_stock
            product.save()

            return self.create(
                product=product,
                previous_stock=previous_stock,
                new_stock=new_stock,
                change_type=change_type,
                quantity=quantity
            )

    history = StockHistoryManager()

    def __str__(self):
        return f"{self.product} {self.change_type} {self.date}"
