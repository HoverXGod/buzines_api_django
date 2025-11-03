import time
from django.test import TestCase
from django.core.cache import cache


class RedisPerformanceTest(TestCase):
    """Тест производительности Redis"""

    def setUp(self):
        self.test_data = {
            'string': 'test_string_value',
            'number': 42,
            'list': [1, 2, 3, 4, 5],
            'dict': {'key': 'value', 'number': 123}
        }

    def test_redis_read_write_speed(self):
        """Тест скорости записи/чтения"""
        operations = 100
        start_time = time.time()

        try:
            # Запись
            for i in range(operations):
                cache.set(f'perf_test_{i}', self.test_data, timeout=60)

            # Чтение
            for i in range(operations):
                value = cache.get(f'perf_test_{i}')
                self.assertEqual(value, self.test_data)

            end_time = time.time()
            total_time = end_time - start_time
            ops_per_second = operations * 2 / total_time  # запись + чтение

            print(f"✅ {operations} операций записи/чтения за {total_time:.2f} сек")
            print(f"✅ Производительность: {ops_per_second:.2f} оп/сек")

            # Проверяем что производительность адекватна
            self.assertGreater(ops_per_second, 10, "Слишком низкая производительность Redis")

        except Exception as e:
            self.fail(f"❌ Ошибка теста производительности: {e}")