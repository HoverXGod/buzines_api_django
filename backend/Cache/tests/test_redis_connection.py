from django.test import TestCase
from django.core.cache import cache
from django.conf import settings

class RedisConnectionTest(TestCase):
    """Тест подключения к Redis"""

    def test_redis_connection(self):
        """Проверка базового подключения к Redis"""
        try:
            # Пробуем записать и прочитать тестовое значение
            test_key = "test_connection"
            test_value = "Hello, Redis!"

            cache.set(test_key, test_value, timeout=10)
            retrieved_value = cache.get(test_key)

            self.assertEqual(retrieved_value, test_value)
            print("✅ Redis подключение работает корректно")

        except Exception as e:
            self.fail(f"❌ Ошибка подключения к Redis: {e}")

    def test_redis_ping(self):
        """Проверка команды PING"""
        try:
            # Для Redis backend можно использовать ping()
            if hasattr(cache, 'ping'):
                result = cache.ping()
                self.assertTrue(result)
                print("✅ Redis PING команда работает")
            else:
                # Альтернативный способ проверки
                cache.set('ping_test', 'pong', 1)
                self.assertEqual(cache.get('ping_test'), 'pong')
                print("✅ Redis доступен через set/get")

        except Exception as e:
            self.fail(f"❌ Redis PING failed: {e}")