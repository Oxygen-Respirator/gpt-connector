from django.core.management.base import BaseCommand

from domain.message_queue.utils import Kafka


class Command(BaseCommand):
    help = 'Subscribe kafka MQ'

    def handle(self, *args, **kwargs):
        kafka_instance = Kafka()
        kafka_instance.setup_consumer()
        kafka_instance.consume_message()


