import datetime

from confluent_kafka import Consumer
from flask import json
import redis

from db.model import *
from library.delete_redis import  Delete_redis_keys_with_prefix

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cấu hình consumer
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_update_user',
    'auto.offset.reset': 'earliest'
}

# Khởi tạo consumer
consumer = Consumer(config)

topic_name = 'update_user'
consumer.subscribe([topic_name])


def update_user():
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        else:
            print('Received message: {}'.format(msg.value()))
            data_receive = (msg.value()).decode()
            print(data_receive)
            data = json.loads(data_receive)
            user_data = User.get(User.id == data['id'])
            if user_data:
                for field, value in data.items():
                    setattr(user_data, field, value)
                user_data.updated_at = datetime.datetime.now()
                user_data.updated_by = data['updated_by']
                user_data.save()

                # Xóa data redis các danh sách All Users
                Delete_redis_keys_with_prefix('users')

                # Xóa data redis của User-id
                Delete_redis_keys_with_prefix(f"user_{data['id']}")


if __name__ == "__main__":
    update_user()
