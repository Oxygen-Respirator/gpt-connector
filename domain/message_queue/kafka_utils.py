import environ
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio

from domain.completion import services


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


class Kafka:
    def __init__(self):
        self.consumer = None
        self.producer = None

        env = environ.Env()
        environ.Env.read_env()

        self.broker_address = env('KAFKA_ADDRESS')

    async def setup_producer(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker_address,
        )
        await self.producer.start()

    async def produce_message(self, headers, key, value):
        await self.producer.send(
            'response_chat',
            key=key.encode('UTF-8'),
            value=value.encode('UTF-8'),
            headers=[(k, v.encode('UTF-8')) for k, v in headers.items()]
        )

    async def setup_consumer(self):
        self.consumer = AIOKafkaConsumer(
            'request_chat',
            bootstrap_servers=self.broker_address,
            group_id='gpt_django',
        )
        await self.consumer.start()

    async def consume_message(self):
        timeout = 0.01
        while True:
            try:
                msg = await asyncio.wait_for(self.consumer.getone(), timeout)
                message = msg.value.decode('utf-8')
                print(f"Received: {message}")

                # 헤더 처리
                headers = dict(msg.headers)
                correlation_id = headers.get('correlationId', b'').decode('UTF-8')

                result = await services.completion(message)

                await self.setup_producer()
                await self.produce_message({'correlationId': correlation_id}, '', result)
                await self.close_producer()
            except asyncio.TimeoutError:
                pass

    async def close_consumer(self):
        await self.consumer.stop()

    async def close_producer(self):
        await self.producer.stop()
