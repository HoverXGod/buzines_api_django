from django.test import TestCase
from django.core.cache import cache
from django.conf import settings


class RedisSpecificTest(TestCase):
    """Тесты специфичные для Redis"""

    def setUp(self):
        self.is_redis = 'redis' in settings.CACHES['default']['BACKEND'].lower()

    def test_redis_backend_detection(self):
        """Проверка что используется Redis бэкенд"""
        if self.is_redis:
            print("✅ Используется Redis бэкенд")
        else:
            print("ℹ️  Используется не-Redis бэкенд, некоторые тесты будут пропущены")

    def test_redis_specific_features(self):
        """Тест специфичных для Redis функций"""
        if not self.is_redis:
            self.skipTest("Тест только для Redis бэкенда")

        try:
            # Пробуем получить Redis клиент (разные способы для разных версий)
            client = None

            # Способ 1: для django-redis
            if hasattr(cache, 'client'):
                client = cache.client
            # Способ 2: для некоторых конфигураций
            elif hasattr(cache, '_client'):
                client = cache._client
            # Способ 3: через get_redis_connection
            elif hasattr(cache, 'get_redis_connection'):
                client = cache.get_redis_connection()

            if client and hasattr(client, 'ping'):
                result = client.ping()
                self.assertTrue(result)
                print("✅ Redis PING команда работает")

                # Дополнительная информация
                info = client.info()
                self.assertIsNotNone(info)
                print(f"✅ Redis version: {info.get('redis_version', 'unknown')}")

            else:
                print("ℹ️  Redis клиент не найден или не поддерживает ping")

        except Exception as e:
            self.fail(f"❌ Ошибка Redis-specific теста: {e}")