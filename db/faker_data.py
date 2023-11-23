from peewee import Model, PostgresqlDatabase, AutoField, CharField, IntegerField, DateTimeField, ForeignKeyField, \
    IntegrityError
from playhouse.db_url import connect
from faker import Faker
from datetime import datetime

from db.model import User

fake = Faker()


def generate_fake_data():
    return {
        "name": fake.name(),
        "age": fake.random_int(min=18, max=99),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "email": fake.email(),
        "role": fake.random_int(min=4, max=4),
        "username": f"user_{fake.user_name()}_{fake.random_int(1, 1000000)}",  # Thêm số ngẫu nhiên để đảm bảo tính duy nhất
        "password": fake.password(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": fake.user_name(),
        "updated_by": fake.user_name(),
    }


# Tạo và lưu 100 bản ghi mẫu vào database
for _ in range(1000000):
    user_data = generate_fake_data()
    try:
        # Tạo và lưu bản ghi mới
        User.create(**user_data)
    except IntegrityError as e:
        # Xử lý ngoại lệ, ví dụ: tạo lại `username` và thử lại
        user_data['username'] = fake.user_name()
        User.create(**user_data)
