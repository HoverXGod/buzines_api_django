from django.core.cache import cache
from functools import wraps


def cache_method(func, timeout=60*60*18):
    def decorator(*args, **kwargs):
        cache_key = f"{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"

        result = cache.get(cache_key)
        if result is None:
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)

        return result

    return decorator