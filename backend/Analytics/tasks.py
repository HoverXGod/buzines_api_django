from celery import shared_task
from datetime import datetime
from Payment.services import get_method
from django.apps import apps
from .models import *
from .managers import *

@shared_task(bind=True, name='Analytics.tasks.clv_update')
def clv_update(self, cls: type[str]):
    clv = apps.get_model('Analytics.CustomerLifetimeValue')
    user = (apps.get_model('User.User')
            .objects.get(id=cls))

    try:
        clv = clv.objects.get(user=user)
    except ObjectDoesNotExist:
        raise ValueError("CLV record for this user does not exist.")

    clv_data = clv.objects._calculate_clv_data(user)
    for field, value in clv_data.items():
        setattr(clv, field, value)
    clv.save()
    return clv

@shared_task(bind=True, name='Analytics.tasks.sf_update')
def sf_update(self, entry_id, **kwargs):

    sf = apps.get_model('Analytics.SalesFunnel')
    allowed_fields = {'stage', 'session_data', 'device_type', 'order_item'}

    try:
        entry = sf.objects.get(id=entry_id)

        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(entry, field, value)
        entry.full_clean()
        entry.save()
        return entry

    except DoesNotExist:
        return None

    except Exception as e:
        raise ValueError(f"Error updating entry: {str(e)}")

@shared_task(bind=True, name='Analytics.pp_update')
def pp_update(self, instance_id, **kwargs):
    instance = (apps.get_model('Analytics.ProductPerformance')
          .objects.get(instance_id))

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
        pp.objects._recalculate_metrics(instance)

    instance.save()
    return instance

@shared_task(bind=True, name='Analytics.tasks.payment_analysis')
def payment_analysis(self, payment_id):
    payment = (apps.get_model("Payment.Payment")
               .objects.get(id = payment_id))

    payment_manager = PaymentAnalysisManager

    # Проверка статуса платежа
    if payment.is_payment:
        return None  # Анализ только для успешных платежей

    # Вычисляем показатели
    gateway_perf = payment_manager._calculate_gateway_performance(payment)
    fraud_indicators = payment_manager._detect_fraud_indicators(payment)
    risk_score = payment_manager._calculate_risk_score(fraud_indicators, payment)
    chargeback_prob = payment_manager._predict_chargeback(payment, risk_score)

    # Создаем или обновляем запись
    analysis, created = payment_manager.get_or_create(
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

@shared_task(bind=True, name='Analytics.tasks.cohort_analysis')
def cohort_analysis(self):
    cohort_model_manager = CohortAnalysisManager()
    today = timezone.now().date()
    cohort_date = today - timezone.timedelta(days=31)
    retention_day = (today - cohort_date).days

    # Определяем основную категорию
    primary_category = (cohort_model_manager
                        ._get_primary_category(cohort_date, retention_day))

    # Создаем или обновляем запись
    cohort, created = cohort_model_manager.get_or_create(
        cohort_date=cohort_date,
        retention_day=retention_day,
        primary_category=primary_category,
        defaults={'metrics': {}}
    )

    # Обновляем метрики
    try:
        metrics = (cohort_model_manager
                   ._calculate_metrics(cohort_date, retention_day, primary_category))
        if cohort.metrics != metrics:
            cohort.metrics = metrics
            cohort.save(update_fields=['metrics'])
    except:
        pass
    return cohort

@shared_task(bind=True, name='Analytics.tasks.order_analysis')
def order_analysis(self, order_id):

    order = (apps.get_model("Order.Order")
               .objects.get(id = order_id))

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

@shared_task(bind=True, name='Analytics.tasks.order_item_analysis')
def order_item_analysis(self, order_item_id, **extra_fields):
    order_item = (apps.get_model("Order.OrderItem")
             .objects.get(id = order_item_id))
    order_item_manager = OrderItemAnalyticsManager()

    # Базовые расчеты
    cost_price = order_item.product.cost_price
    price = order_item.product.price
    margin = price - cost_price

    # Расчет комплексных показателей
    profitability_index = (margin / cost_price * 100) if cost_price > 0 else 0

    # Расчет времени доставки (пример реализации)
    delivery_time = self._calculate_delivery_time(order_item)

    # Определение сопутствующих товаров
    cross_sell_products = self._find_cross_sell_products(order_item)

    # Создание объекта
    return order_item_manager.create(
        order_item=order_item,
        margin=margin,
        profitability_index=profitability_index,
        delivery_time=delivery_time,
        **extra_fields
    ).cross_sell_products.add(*cross_sell_products)
