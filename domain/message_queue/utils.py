import environ
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from domain.completion import services
import time


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

    def setup_producer(self):
        producer_conf = {
            'bootstrap.servers': self.broker_address,
        }

        self.producer = Producer(producer_conf)

    def produce_message(self, headers, key, value):
        self.producer.produce('response_chat', headers=headers, key=key.encode('UTF-8'), value=value.encode('UTF-8'),
                              callback=delivery_report)
        self.producer.flush()

    def setup_consumer(self):
        consumer_conf = {
            'bootstrap.servers': self.broker_address,
            'group.id': 'gpt',
            'auto.offset.reset': 'earliest'
        }

        self.consumer = Consumer(consumer_conf)
        self.consumer.subscribe(['request_chat'])

    def consume_message(self):
        while True:
            msg = self.consumer.poll(1)

            if msg is None:
                print('Message does not exist')
                continue

            if msg.error():
                print(f"Consumer error: {msg.error()}")
                raise KafkaException(msg.error())
            else:
                message = msg.value().decode('utf-8')
                print(f"Received: {message}")

                # 헤더 처리
                headers = msg.headers()

                if headers is None:
                    continue

                correlation_id = None
                for key, value in headers:
                    if key == 'correlationId':
                        correlation_id = value.decode('utf-8')
                        break

                result = services.completion(message)

                self.setup_producer()
                self.produce_message({'correlationId': correlation_id}, '', result)

    def close_consumer(self):
        self.consumer.close()
