from django.test import TestCase
import pika
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRabbitMQConnection(TestCase):
    def setUp(self):
        self.connection_params = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=pika.PlainCredentials('guest', 'guest'),
            heartbeat=600,
            blocked_connection_timeout=300
        )

    def test_basic_connection(self):
        """Тест базового подключения к RabbitMQ"""
        connection = None
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()

            self.assertTrue(connection.is_open)
            self.assertTrue(channel.is_open)
            logger.info("✅ Basic connection test PASSED")

        except Exception as e:
            self.fail(f"Connection failed: {e}")
        finally:
            if connection and connection.is_open:
                connection.close()

    def test_channel_operations(self):
        """Тест операций с каналом"""
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()

        try:
            # Тест объявления очереди
            queue_declare = channel.queue_declare(queue='test_queue', durable=True)
            self.assertIsNotNone(queue_declare)

            # Тест отправки сообщения
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body='Test message',
                properties=pika.BasicProperties(delivery_mode=2)  # persistent
            )
            logger.info("✅ Channel operations test PASSED")

        finally:
            # Очистка
            channel.queue_delete(queue='test_queue')
            connection.close()

    def test_connection_with_timeout(self):
        """Тест подключения с таймаутом"""
        try:
            connection = pika.BlockingConnection(self.connection_params)
            # Проверяем что соединение активно через 2 секунды
            time.sleep(2)
            self.assertTrue(connection.is_open)
            connection.close()
            logger.info("✅ Connection timeout test PASSED")

        except pika.exceptions.AMQPConnectionError as e:
            self.fail(f"Connection timeout failed: {e}")