from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

def get_cache_key(func, *args, **kwargs):
    cache_key = f"{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"

def get_cache_used_models() -> list:
    cache_key = "use_cache_models_disability"
    result = cache.get(cache_key)
    return [] if result is None else result

def conf_used_cache_models(cache_key_method, use_models: list):
    resolved_models = []
    for model in use_models:
        if isinstance(model, str):
            resolved_models.append(apps.get_model(model))
        else:
            resolved_models.append(model)
    use_models = resolved_models

    cache_key = "use_cache_models_disability"
    timeout = 60*60*24
    result = [item._meta.model_name for item in use_models]

    instance = get_cache_used_models()

    equal = False

    for item in result:
        if item not in instance:
            instance.append(item)
            equal = True

    if equal:
        cache.set(cache_key, instance, timeout)

    list_caches = cache.get("caches_list")
    if list_caches is None: list_caches = []

    list_caches.append([result, cache_key_method])
    cache.set("caches_list", list_caches, timeout)

@receiver(post_save, sender="User.User")
@receiver(post_save, sender="Api_Keys.Api_key")
@receiver(post_save, sender="Content.Post")
@receiver(post_save, sender="Content.PageText")
@receiver(post_save, sender="Order.Order")
@receiver(post_save, sender="Product.Product")
@receiver(post_save, sender="Product.Category")
@receiver(post_save, sender="Product.UserSubscriptionItem")
@receiver(post_save, sender="User.UserGroup")
def core_cache(sender, instance, **kwargs):
    cache_key = "use_cache_models_disability"
    timeout = 60 * 60 * 24
    model_name = instance._meta.model_name

    instance_cache = get_cache_used_models()

    if model_name in instance_cache:
        instance_cache.remove(model_name)

    list_caches = cache.get("caches_list")
    if list_caches is None: list_caches = [[[],[]]]

    for item in list_caches:
        if model_name in item[0]:
            cache.delete(item[1])
            list_caches.remove(item)

    cache.set(cache_key, instance_cache, timeout)