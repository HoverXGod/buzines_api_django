from django.db import models
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from Order.models import OrderItem
from Payment.models import Payment
from decimal import Decimal

class CustomerLifetimeValueManager(models.Manager):

    def _calculate_clv_data(self, user):
        """
        Вычисляет данные для CLV на основе заказов пользователя.
        Возвращает словарь с полями: total_spent, avg_order_value, 
        purchase_frequency, preferred_category, category_spend.
        """
        # Получаем все заказы пользователя
        orders = user.orders.annotate(order_total=Sum('items__price'))

        # Общая сумма потраченных средств
        total_spent = orders.aggregate(total=Sum('order_total'))['total'] or 0

        # Средний чек (avg_order_value)
        order_count = orders.count()
        avg_order_value = total_spent / order_count if order_count > 0 else 0

        # Частота покупок (заказов в месяц)
        first_order = orders.order_by('date').first()
        if first_order:
            months_since_first = (timezone.now().year - first_order.date.year) * 12 \
                                + (timezone.now().month - first_order.date.month)
            purchase_frequency = order_count / max(months_since_first, 1) * 12  # Нормализуем до годовой
        else:
            purchase_frequency = 0

        # Самая популярная категория и траты в ней
        category_data = (
            OrderItem.objects
            .filter(order__user=user)
            .values('product__category')
            .annotate(total_spent=Sum('price'))
            .order_by('-total_spent')
            .first()
        )

        preferred_category = category_data['product__category'] if category_data else None
        category_spend = category_data['total_spent'] if category_data else 0

        return {
            'total_spent': total_spent,
            'avg_order_value': avg_order_value,
            'purchase_frequency': purchase_frequency,
            'preferred_category_id': preferred_category,
            'category_spend': category_spend
        }

    def create_clv(self, user):
        """Автоматически создает запись CLV с вычисленными значениями"""
        if self.filter(user=user).exists():
            raise ValueError("CLV record for this user already exists.")
        
        clv_data = self._calculate_clv_data(user)
        return self.create(
            user=user,
            **clv_data
        )

    def update_clv(self, user):
        """Обновляет существующую запись CLV новыми вычисленными значениями"""
        try:
            clv = self.get(user=user)
        except ObjectDoesNotExist:
            raise ValueError("CLV record for this user does not exist.")
        
        clv_data = self._calculate_clv_data(user)
        for field, value in clv_data.items():
            setattr(clv, field, value)
        clv.save()
        return clv

class SalesFunnelManager(models.Manager):
    """Кастомный менеджер для работы с воронкой продаж"""
    
    def add_entry(self, user, product, stage, **kwargs):
        """
        Добавление новой записи в воронку
        """
        required_fields = {'user', 'product', 'stage'}
        if not all([user, product, stage]):
            raise ValueError("Missing required fields: user, product, stage")

        try:
            entry = self.model(
                user=user,
                product=product,
                stage=stage,
                category=product.category if product else None,
                device_type=kwargs.get('device_type', 'desktop'),
                session_data=kwargs.get('session_data', {}),
                order_item=kwargs.get('order_item')
            )
            entry.full_clean()
            entry.save()
            return entry
        except Exception as e:
            raise ValueError(f"Error creating funnel entry: {str(e)}")

    def update_entry(self, entry_id, **kwargs):
        """
        Обновление существующей записи
        """
        allowed_fields = {'stage', 'session_data', 'device_type', 'order_item'}
        try:
            entry = self.get(id=entry_id)
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(entry, field, value)
            entry.full_clean()
            entry.save()
            return entry
        except self.model.DoesNotExist:
            return None
        except Exception as e:
            raise ValueError(f"Error updating entry: {str(e)}")

    def get_entries(self, user=None, product=None, category=None, 
                  stage=None, days_back=30, limit=100):
        """
        Получение записей с фильтрами
        """
        filters = Q()
        
        if user:
            filters &= Q(user=user)
        if product:
            filters &= Q(product=product)
        if category:
            filters &= Q(category=category)
        if stage:
            filters &= Q(stage=stage)
            
        date_threshold = timezone.now() - timedelta(days=days_back)
        filters &= Q(timestamp__gte=date_threshold)

        return self.filter(filters)\
            .select_related('user', 'product', 'category')\
            .order_by('-timestamp')[:limit]

class PerformanceManager(models.Manager):
    def add_entry(self, product, date=None, **kwargs):
        """Создание записи с автоматическим расчетом метрик"""
        date = date or timezone.now().date()
        
        entry_data = {
            'product': product,
            'category': product.category,
            'date': date,
            **kwargs
        }
        
        # Автоматический расчет показателей
        entry_data = self._calculate_initial_metrics(product, date, entry_data)
        entry = self.model(**entry_data)
        
        # Блокировка стандартного создания
        entry.save(using=self._db)
        return entry

    def update_entry(self, instance, **kwargs):
        """Обновление записи с перерасчетом метрик"""
        force_recalculate = False
        
        # Если изменились продукт или дата - требуется полный перерасчет
        if 'product' in kwargs or 'date' in kwargs:
            force_recalculate = True
            if 'product' in kwargs:
                instance.product = kwargs.pop('product')
                instance.category = instance.product.category
            if 'date' in kwargs:
                instance.date = kwargs.pop('date')
        
        # Обновление полей
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        
        # Перерасчет метрик при необходимости
        if force_recalculate or any(field in kwargs for field in ['metrics', 'total_units_sold']):
            self._recalculate_metrics(instance)
        
        instance.save()
        return instance

    def _calculate_initial_metrics(self, product, date, data):
        """Расчет начальных метрик при создании записи"""

        # Базовые метрики
        metrics = data.get('metrics', {})
        metrics.setdefault('views', 0)
        metrics.setdefault('cart_adds', 0)
        metrics.setdefault('purchases', 0)
        metrics.setdefault('stock_level', product.stock)
        
        # Агрегация данных из OrderItem
        order_data = OrderItem.objects.filter(
            product=product,
        ).aggregate(
            total_units=Sum('quanity'),
            avg_price=Avg('price'),
            total_discount=Sum('discount')
        )
        
        data.update({
            'total_units_sold': order_data['total_units'] or 0,
            'avg_selling_price': order_data['avg_price'] or Decimal('0.00'),
            'discount_impact': order_data['total_discount'] or Decimal('0.00'),
            'metrics': metrics
        })
        
        # Расчет коэффициента конверсии
        data['metrics']['conversion_rate'] = self._calculate_conversion_rate(
            data['metrics']['purchases'],
            data['metrics']['views']
        )
        
        return data

    def _recalculate_metrics(self, instance):
        """Перерасчет всех метрик для существующей записи"""
        instance.update_metrics()  # Используем метод модели
        instance.update_conversion_rate()  # Используем метод модели

    @staticmethod
    def _calculate_conversion_rate(purchases, views):
        """Расчет коэффициента конверсии"""
        return round(purchases / views * 100, 2) if views > 0 else 0.0

class CohortAnalysisManager(models.Manager):
    def add_entry(self):
        """Автоматически создает запись когорты на основе вчерашних данных"""
        # Определяем даты
        today = timezone.now().date()
        cohort_date = today - timezone.timedelta(days=31)
        retention_day = (today - cohort_date).days
        
        # Определяем основную категорию
        primary_category = self._get_primary_category(cohort_date, retention_day)
        
        # Создаем или обновляем запись
        cohort, created = self.get_or_create(
            cohort_date=cohort_date,
            retention_day=retention_day,
            primary_category=primary_category,
            defaults={'metrics': {}}
        )
        
        # Обновляем метрики
        metrics = self._calculate_metrics(cohort_date, retention_day, primary_category)
        if cohort.metrics != metrics:
            cohort.metrics = metrics
            cohort.save(update_fields=['metrics'])
        
        return cohort

    def _get_primary_category(self, cohort_date, retention_day):
        """Определяет основную категорию по заказам за указанную дату"""
        from Order.models import OrderItem
        from Product.models import Category

        end_date = cohort_date + timezone.timedelta(days=retention_day)
        
        # Анализ категорий в заказах за дату
        category_counts = (
            OrderItem.objects
            .filter(order__date__range=(cohort_date, end_date))
            .values('product__category')
            .annotate(total=Count('product__category'))
            .order_by('-total')
        )

        if category_counts: 
            return Category.objects.get(id=category_counts[0]['product__category'])
        else: return None

    def _calculate_metrics(self, cohort_date, retention_day, category):
        """Вычисляет метрики для когорты"""
        from User.models import User
        from Order.models import Order
        
        # Расчет временного периода
        end_date = cohort_date + timezone.timedelta(days=retention_day)
        
        # Пользователи когорты
        cohort_users = User.objects.filter(
            date_joined__range=(cohort_date, end_date),
        )
        
        # Заказы когорты
        orders = Order.objects.filter(
            date__date__range=(cohort_date, end_date)
        )
        
        # Основные метрики
        total_users = cohort_users.count()
        active_users = cohort_users.filter(last_login__date__lte=end_date).count()
        
        order_stats = orders.aggregate(
            total_revenue=Sum('payment__cost'),
            avg_order_value=Sum('payment__cost') / Count('id'),
            total_orders=Count('id')
        )
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'revenue': int(order_stats['total_revenue']) or 0.0,
            'avg_order_value': int(order_stats['avg_order_value']) or 0.0,
            'orders_count': order_stats['total_orders'],
            'arppu': int(order_stats['total_revenue'] / active_users) if active_users else 0.0,
        }

class PaymentAnalysisManager(models.Manager):
    def add_entry(self, payment):
        """Автоматически создает и заполняет анализ платежа"""
        # Проверка статуса платежа
        if payment.is_payment:
            return None  # Анализ только для успешных платежей

        # Вычисляем показатели
        gateway_perf = self._calculate_gateway_performance(payment)
        fraud_indicators = self._detect_fraud_indicators(payment)
        risk_score = self._calculate_risk_score(fraud_indicators, payment)
        chargeback_prob = self._predict_chargeback(payment, risk_score)

        # Создаем или обновляем запись
        analysis, created = self.get_or_create(
            payment=payment,
            defaults={
                'gateway_performance': gateway_perf,
                'fraud_indicators': fraud_indicators,
                'risk_score': risk_score,
                'chargeback_probability': chargeback_prob
            }
        )
        
        # Обновление существующей записи
        if not created:
            analysis.gateway_performance = gateway_perf
            analysis.fraud_indicators = fraud_indicators
            analysis.risk_score = risk_score
            analysis.chargeback_probability = chargeback_prob
            analysis.save()

        return analysis

    def _calculate_gateway_performance(self, payment):
        """Время обработки платежного шлюза"""
        if payment.created_time and payment.processed_at:
            return (payment.processed_at - payment.created_time).total_seconds()
        return None

    def _detect_fraud_indicators(self, payment):
        """Выявление признаков мошенничества с учетом новой структуры"""
        indicators = {}
        
        # Проверка суммы (используем Decimal для точных расчетов)
        avg_amount = payment.user.payments.aggregate(
            avg=models.Avg('cost')
        )['avg'] or Decimal('0.00')

        if payment.pay_time == None:
            payment.pay_time = payment.created_time
        
        indicators['high_amount'] = payment.cost > avg_amount * Decimal('3')
        indicators['non_working_hours'] = not (9 <= payment.pay_time.hour < 20)
        
        # Проверка валюты
        indicators['currency_mismatch'] = (
            payment.currency != payment.user.default_currency
        )
        
        # Повторные попытки (используем payment_id для отслеживания)
        indicators['multiple_attempts'] = (
            Payment.objects.filter(
                Q(payment_id__startswith=payment.payment_id[:16]) &
                Q(created_time__gte=payment.created_time - timezone.timedelta(hours=1))
            ).count() > 3)

        return indicators

    def _calculate_risk_score(self, indicators, payment):
        """Обновленная формула расчета риска"""
        score = 0
        weights = {
            'high_amount': 25,
            'currency_mismatch': 20,
            'multiple_attempts': 30,
            'non_working_hours': 15,
            'payment_gateway_risk': 10
        }
        
        # Дополнительный риск для определенных шлюзов
        if payment.payment_gateway in ['high_risk_gateway1', 'high_risk_gateway2']:
            score += weights['payment_gateway_risk']
        
        for indicator, value in indicators.items():
            if value and indicator in weights:
                score += weights[indicator]
        
        return min(score, 100)

    def _predict_chargeback(self, payment, risk_score):
        """Прогнозирование с учетом исторических данных"""
        base_prob = risk_score * 0.8
        
        # Учет фактических возвратов
        if payment.chargeback_status:
            return min(base_prob + 20, 100)
            
        # Учет комиссии
        if payment.fee > payment.cost * Decimal('0.1'):
            base_prob += 10
        
        return min(base_prob, 100)
    
class OrderAnalyticsManager(models.Manager):
    def add_entry(self, order):
        """Создает или обновляет аналитическую запись для заказа"""
        # Вычисляем основные показатели
        margin = self._calculate_margin(order)
        acquisition_source = self._determine_acquisition_source(order)
        customer_journey = self._analyze_customer_journey(order)
        churn_risk = self._predict_churn_risk(order)
        
        # Создаем или обновляем запись
        analytics, created = self.get_or_create(
            order=order,
            defaults={
                'margin': margin,
                'acquisition_source': acquisition_source,
                'customer_journey': customer_journey,
                'predicted_churn_risk': churn_risk
            }
        )
        
        # Если запись существовала - обновляем данные
        if not created:
            analytics.margin = margin
            analytics.acquisition_source = acquisition_source
            analytics.customer_journey = customer_journey
            analytics.predicted_churn_risk = churn_risk
            analytics.save()
        
        # Анализируем товарные метрики
        self._analyze_items(analytics)
        
        return analytics

    def _calculate_margin(self, order):
        """Расчет маржинальности заказа"""
        total_cost = sum(
            item.quanity * item.product.cost_price
            for item in order.items.all()
        )
        return abs(float(order.payment.amount) - total_cost)

    def _determine_acquisition_source(self, order):
        """Определение источника привлечения"""
        user = order.user
        if user:
            return user.acquisition_source or 'unknown'
        return 'direct'

    def _analyze_customer_journey(self, order):
        """Анализ пути клиента"""
        journey = {}
        user = order.user
        
        if user:
            # Время от регистрации до первого заказа
            first_order = user.orders.order_by('date').first()
            if first_order and first_order == order:
                journey['days_to_first_order'] = (
                    order.date - user.date_joined
                ).days
            
            # Активность перед заказом
            journey['pre_order_visits'] = user.visits.filter(
                timestamp__range=(
                    order.date - timedelta(days=7),
                    order.date
            )).count()
            
            # История заказов
            journey['total_orders'] = user.orders.count()
        
        return journey

    def _predict_churn_risk(self, order):
        """Прогноз риска оттока"""
        if not order.user:
            return 0.0
            
        last_order_days = (timezone.now() - order.user.orders.latest(
            'date').date).days
        order_count = order.user.orders.count()
        
        # Простая эвристическая модель
        risk = min(
            (last_order_days * 0.5) + (50 / order_count if order_count > 0 else 0), 100
        )
        return round(risk, 2)

    def _analyze_items(self, analytics):
        """Анализ товарных метрик"""
        items = analytics.order.items.all()
        
        # Топ товаров
        top_items = items.values(
            'product__id', 'product__name').annotate(
                total_units=Sum('quanity')).order_by('-total_units')[:5]
        
        # Индекс разнообразия
        unique_products = items.values('product').distinct().count()
        diversity = unique_products / items.count() if items.count() > 0 else 0
        
        analytics.item_metrics = {
            'top_items': list(top_items),
            'basket_diversity': round(diversity, 2)
        }
        analytics.save()

class InventoryTurnoverManager(models.Manager):
    def add_entry(self, product):
        today = timezone.now().date()
        period_start = today.replace(day=1)
        
        # Рассчитываем конец периода
        if period_start.month == 12:
            next_month = period_start.replace(year=period_start.year+1, month=1)
        else:
            next_month = period_start.replace(month=period_start.month+1)
        period_end = next_month - timedelta(days=1)

        # Проверка существующей записи
        if self.filter(product=product, period_start=period_start).exists():
            return

        # Получаем общее количество продаж за период
        total_sold = (
            product.orders.filter(
                order__created_date__gte=period_start,
                order__created_date__lte=period_end
            ).aggregate(total=Sum('quanity'))['total'] or 0
        )

        # Рассчитываем дни отсутствия товара
        stockout_days = self.calculate_stockout_days(product, period_start, period_end)

        # Расчет оборачиваемости
        avg_stock = self.calculate_avg_stock(product, period_start, period_end)
        stock_turnover = total_sold / avg_stock if avg_stock > 0 else 0

        self.create(
            product=product,
            category=product.category,
            period_start=period_start,
            period_end=period_end,
            stock_turnover=round(stock_turnover, 2),
            stockout_days=stockout_days,
            demand_forecast=total_sold
        )

    def calculate_avg_stock(self, product, start, end):
        from .models import StockHistory
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

    def calculate_stockout_days(self, product, start, end):
        from .models import StockHistory
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

class OrderItemAnalyticsManager(models.Manager):
    def create_analytics(self, order_item, **extra_fields):
        """
        Создает аналитическую запись с автоматическим расчетом показателей
        """
        # Базовые расчеты
        cost_price = order_item.product.cost_price
        price = order_item.price_at_purchase
        margin = price - cost_price
        
        # Расчет комплексных показателей
        profitability_index = (margin / cost_price * 100) if cost_price > 0 else 0
        
        # Расчет времени доставки (пример реализации)
        delivery_time = self._calculate_delivery_time(order_item)
        
        # Определение сопутствующих товаров
        cross_sell_products = self._find_cross_sell_products(order_item)
        
        # Создание объекта
        return self.create(
            order_item=order_item,
            margin=margin,
            profitability_index=profitability_index,
            delivery_time=delivery_time,
            **extra_fields
        ).cross_sell_products.add(*cross_sell_products)
    
    def _calculate_delivery_time(self, order_item):
        """Рассчитывает время доставки в днях"""
        if hasattr(order_item.order, 'delivery_date'):
            delta = order_item.order.delivery_date - order_item.order.order_date
            return delta.days
        return 0
    
    def _find_cross_sell_products(self, order_item):
        """Находит часто покупаемые вместе товары"""
        from .models import OrderItem
        
        # Получаем все заказы, где был этот товар
        order_ids = OrderItem.objects.filter(
            product=order_item.product
        ).values_list('order_id', flat=True)
        
        # Находим товары из тех же заказов
        cross_sell = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(
            product=order_item.product
        ).values('product').annotate(
            total=Count('product')
        ).order_by('-total')[:3]
        
        return [item['product'] for item in cross_sell]

