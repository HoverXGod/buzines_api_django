from functools import wraps
from business_api.celery import app as celery_app
import logging

logger = logging.getLogger(__name__)

def task(max_retries=30, retry_delay=15, total_timeout=900):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            task = celery_app.send_task(
                f'{func.__module__}.{func.__name__}',
                args=args,
                kwargs=kwargs,
                retry=True,
                retry_policy={
                    'max_retries': max_retries,
                    'interval_start': retry_delay,
                    'interval_step': retry_delay,
                    'interval_max': retry_delay,
                }
            )
            return task

        wrapper.delay = wrapper

        return wrapper

    return decorator
