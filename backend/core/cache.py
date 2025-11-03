from django.core.cache import cache
from Cache.disability import conf_used_cache_models, get_cache_used_models
from BaseSecurity.models import ExceptionManager
from functools import wraps
from django.apps import apps

def cache_api_view(use_models: list, timeout=60 * 60 * 18, cache_exceptions=False):

    def wrapper(func):
        def decorator(*args, **kwargs):
            from BaseSecurity.services import SecureResponse

            key_parts = [
                func.__module__ or 'global',
                func.__name__,
                str(args),
                str(tuple(sorted(kwargs.items())))
            ]
            cache_key = ':'.join(key_parts)

            result = cache.get(cache_key)
            if result is None:

                result = func(*args, **kwargs)
                if result.status in [200, 201, 202, 203]:
                    cache.set(cache_key, [result.data, result.status], timeout)

                # except Exception as e:
                #     if cache_exceptions:
                #         error_result = {"__cache_exception__": True, "error": str(e)}
                #         cache.set(cache_key, error_result, min(timeout, 300))
                #
                #     ExceptionnManager.register_exception(e)
                #     raise Exception(f"{func.__name__} Error. Details in Admin Panel")
            else:
                if isinstance(result, dict) and result.get("__cache_exception__"):
                    raise Exception(f"Cached exception: {result['error']} Cache key: {cache_key}")

                if use_models:
                    conf_used_cache_models(cache_key, use_models)

                return SecureResponse(status=result[1], data=result[0])

            return result

        return decorator

    return wrapper

def cache_method(use_models: list, timeout=60 * 60 * 18, cache_exceptions=False):

    def wrapper(func):

        if hasattr(func, '__func__'):
            func = func.__func__
        else:
            func = func

        def decorator(*args, **kwargs):

            key_parts = [
                func.__module__ or 'global',
                func.__name__,
                str(args),
                str(tuple(sorted(kwargs.items())))
            ]
            cache_key = ':'.join(key_parts)

            result = cache.get(cache_key)
            if result is None:
                try:
                    result = func(*args, **kwargs)
                    cache.set(cache_key, result, timeout)

                except Exception as e:
                    if cache_exceptions:
                        error_result = {"__cache_exception__": True, "error": str(e)}
                        cache.set(cache_key, error_result, min(timeout, 300))

                    ExceptionManager.register_exception(e)
                    raise Exception(f"{func.__name__} Error. Details in Admin Panel")
            else:
                if isinstance(result, dict) and result.get("__cache_exception__"):
                    raise Exception(f"Cached exception: {result['error']} Cache key: {cache_key}")

                if use_models:
                    conf_used_cache_models(cache_key, use_models)

            return result

        return decorator

    return wrapper