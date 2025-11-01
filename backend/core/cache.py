from django.core.cache import cache
from Cache.disability import conf_used_cache_models, get_cache_used_models
from functools import wraps

def cache_api_view(use_models: list, timeout=60 * 60 * 18):

    def wrapper(func):
        def decorator(*args, **kwargs):
            from BaseSecurity.services import SecureResponse
            cache_key = f"{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"

            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                if result.status in [200, 201, 202, 203]:
                    cache.set(cache_key, [result.data, result.status], timeout)
            else:
                conf_used_cache_models(cache_key, use_models)
                return SecureResponse(status=result[1], data=result[0])
            return result

        return decorator

    return wrapper