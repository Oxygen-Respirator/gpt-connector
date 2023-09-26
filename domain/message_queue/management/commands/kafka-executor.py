from django.core.management.base import BaseCommand
import asyncio

from domain.message_queue.kafka_utils import Kafka


class Command(BaseCommand):
    help = 'Subscribe kafka MQ'

    async def handle_async(self, *args, **kwargs):
        kafka_instance = Kafka()

        await kafka_instance.setup_consumer()

        try:
            await kafka_instance.consume_message()
        except KeyboardInterrupt:  # Ctrl+C를 눌러 종료할 경우
            pass
        finally:
            await kafka_instance.close_consumer()

    def handle(self, *args, **kwargs):
        asyncio.run(self.handle_async(*args, **kwargs))
