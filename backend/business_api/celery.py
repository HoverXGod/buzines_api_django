import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_api.settings')

app = Celery('business_api')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks([
    'Payment',
    'Analytics',
    'Order',
    'Content',
    'Tenants',
])

app.conf.update(
    broker_url='amqp://guest:guest@rabbitmq:5672//',
    result_backend='rpc://',  # или 'redis://redis:6379/0' если есть Redis
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

# Автоматическое обнаружение задач
app.autodiscover_tasks()

# Настройки для повторных попыток
app.conf.task_default_retry_delay = 60  # 1 минута
app.conf.task_max_retries = 15  # Максимум 15 попыток
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_max_tasks_per_child = 100
app.conf.worker_disable_rate_limits = False
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'