from confluent_kafka import Producer, Consumer, KafkaError
import environ


class Kafka:
    def __init__(self):
        env = environ.Env()
        environ.Env.read_env()

        self.broker_address = env('KAFKA_ADDRESS')

    def setup_producer(self):
        producer_conf = {
            'bootstrap.servers': self.broker_address,
        }
        self.producer = Producer(producer_conf)

    def produce_message(self, key, value):
        self.producer.produce('chat-django', key=key.encode('utf-8'), value=value.encode('utf-8'), callback=self.delivery_report)
        self.producer.flush()

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def setup_consumer(self):
        consumer_conf = {
            'bootstrap.servers': self.broker_address,
            'group.id': 'gpt',
            'auto.offset.reset': 'earliest',
        }
        self.consumer = Consumer(consumer_conf)

    def consume_message(self, topic):
        self.consumer.subscribe([topic])

        while True:
            msg = self.consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            print(f"Received message: {msg.value().decode('utf-8')}")

    def close_consumer(self):
        self.consumer.close()
