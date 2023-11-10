from confluent_kafka import Producer
import json


class KafkaProducer:
    def __init__(self):
        self.producer_config = {
            'bootstrap.servers': 'localhost:9092'
        }
        self.producer = Producer(self.producer_config)

    def send_message(self, topic_name, message_data):
        data_send = json.dumps(message_data)
        data_send = data_send.encode()
        self.producer.produce(topic=topic_name, value=data_send)
        self.producer.flush()

    def close(self):
        self.producer.flush()

