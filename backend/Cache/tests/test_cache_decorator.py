from django.test import TestCase
from django.core.cache import cache
from core.cache import cache_method

class CacheDecoratorTest(TestCase):
    """Тест работы декоратора кеширования с Redis"""

    def test_cache_method_decorator_with_redis(self):
        """Тест что декоратор корректно работает с Redis"""

        # Временный класс для тестирования
        class TestService:
            call_count = 0

            @cache_method(use_models=[], timeout=10)
            def get_data(self, param):
                self.call_count += 1
                return f"result_for_{param}_{self.call_count}"

        service = TestService()

        # Первый вызов - должен выполниться функция
        result1 = service.get_data('test')
        self.assertEqual(service.call_count, 1)
        self.assertEqual(result1, "result_for_test_1")

        # Второй вызов с теми же параметрами - должен вернуть из кеша
        result2 = service.get_data('test')
        self.assertEqual(service.call_count, 1)  # счетчик не должен увеличиться
        self.assertEqual(result2, "result_for_test_1")

        # Вызов с другими параметрами - снова выполнится функция
        result3 = service.get_data('other')
        self.assertEqual(service.call_count, 2)
        self.assertEqual(result3, "result_for_other_2")

        print("✅ Декоратор кеширования работает корректно с Redis")