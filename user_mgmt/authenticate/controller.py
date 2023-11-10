import datetime

import bcrypt
from flask import Flask, jsonify, request
from marshmallow import ValidationError
from peewee import IntegrityError, DoesNotExist
from flask_jwt_extended import *

from db.model import User
from marshmallow import ValidationError

from library.validate import UserSchemaValidate
from library.delete_redis import Delete_redis_keys_with_prefix
from library.hassed_pass import hash_password


def register_service():
    data = request.get_json()
    # user_schema = UserSchemaValidate()

    try:
        UserSchemaValidate().load(data)
        # validated_data = user_schema.load(data)
    except ValidationError as e:
        return jsonify({"message": "Invalid input data", "errors": e.messages}), 400

    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', '4')  # Default role is 'user'
    updated_at = datetime.datetime.now()
    created_by = name
    updated_by = name
    hashed_password_result = hash_password(password)

    if all(field in data for field in ('name', 'age', 'phone_number', 'email',
                                       'address', 'username', 'hashed_password')):
        return jsonify({'error': 'Cannot create, without field'}), 400

    if any(field in data for field in ('id', 'role', 'created_at', 'created_by', 'updated_at', 'updated_by')):
        return jsonify({'error': 'Cannot create'}), 400

    if User.select().where(User.username == username).exists():
        return jsonify({"message": "Username already exists"}), 400

    # Tạo một bản ghi người dùng mới
    user = User(
        name=name,
        age=age,
        address=address,
        username=username,
        phone_number=phone_number,
        email=email,
        password=hashed_password_result.decode('utf-8'),
        role=role,
        updated_at=updated_at,
        created_by=created_by,
        updated_by=updated_by

    )
    # Xóa dữ liệu redis của all Users
    Delete_redis_keys_with_prefix('users_1')
    user.save()

    return (jsonify({"message": "Registration successful !"}),
            201)


def login_service():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        user = User.get(User.username == username)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity={
                'username': username,
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.id
            })
            return jsonify(access_token=access_token), 200
    except DoesNotExist:
        pass

    return jsonify({"message": "Invalid credentials"}), 401
