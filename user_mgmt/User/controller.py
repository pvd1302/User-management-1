from flask import request, jsonify, json
from flask_jwt_extended import get_jwt_identity, jwt_required
from peewee import *
from playhouse.shortcuts import model_to_dict
from db.model import *
from flask import request, jsonify, json
import redis
from db.mash import UserSchema
from marshmallow import ValidationError
from flask.json import jsonify
import time

import bcrypt

from library.find_name import apply_name_condition
from library.validate import UserSchemaValidate
from library.delete_redis import Delete_redis_keys_with_prefix
from library.hassed_pass import hash_password
from library.pagination import calculate_pagination
from library.constant import ROLE
from db.model import db

from kafka1.producer import KafkaProducer

r = redis.StrictRedis(host='localhost', port=6379, db=0)

producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'client_users'
}


@jwt_required()
class Get_user:
    @staticmethod
    def get_all_user_service():
        # truyền vào thông số phân trang
        page = int(request.args.get('page'))
        if page < 1:
            return jsonify({'message': 'Invalid pagination parameters. Page must be greater than or equal to 1'})
        per_page = int(request.args.get('per_page'))

        # tìm kiếm theo tên
        name_user = request.args.get('name')

        # lấy dữ liệu từ token
        current_user = get_jwt_identity()

        # Lấy dữ liệu từ redis
        if name_user:
            key_list_users = f"users_{current_user['username']}_{page}_{per_page}_{name_user}"
        else:
            key_list_users = f"users_{current_user['username']}_{page}_{per_page}"

        cached_data = r.get(key_list_users)
        if cached_data:
            return jsonify(json.loads(cached_data))


        if current_user['role'] == ROLE.ADMIN:
            start_time = time.time()
            # Admin có quyền xem tất cả danh sách
            users_query = User.select().order_by(User.id)
            # nếu có thêm 'name_user'
            users_query = apply_name_condition(users_query, name_user)
            query_sql = users_query.sql()
            total_users = users_query.count()

            users = users_query.limit(per_page).offset((per_page * page) - per_page)

            print(query_sql)
            end_time = time.time()
            elapsed_time = end_time - start_time

            user_schema = UserSchema(many=True)  # Đặt many=True nếu users là danh sách
            users_json = user_schema.dump(users)

            # users_query = users_query.execute()

            note = 'bạn có thể xem toàn bộ danh sách'

        elif current_user['role'] == ROLE.MANAGER:
            # Manager chỉ xem danh sách các nhóm mình quản lý
            teams = Team.select().where(Team.manager == current_user['id'])
            users_query = User.select().join(TeamMember).where(TeamMember.team << teams).order_by(User.id)
            # nếu có thêm 'name_user'
            users_query = apply_name_condition(users_query, name_user)

            total_users = users_query.count()
            users = users_query.order_by(User.id).limit(per_page).offset((per_page * page) - per_page)
            note = 'bạn có thể xem danh sách bao gồm Leader và User'

        elif current_user['role'] == ROLE.LEADER:
            # Leader chỉ xem danh sách các nhóm mà mình là leader
            teams = Team.select().where(Team.leader == current_user['id'])
            users_query = User.select().join(TeamMember).where(TeamMember.team << teams &
                                                               (User.role != 2)).order_by(User.id)
            # nếu có thêm 'name_user'
            users_query = apply_name_condition(users_query, name_user)

            total_users = users_query.count()
            users = users_query.order_by(User.id).limit(per_page).offset((per_page * page) - per_page)
            note = 'bạn có thể xem danh sách thành viên trong Team của bạn'

        else:
            # User chỉ xem thông tin của bản thân mình
            total_users = 1
            users = (User.select().where(User.id == current_user['id']))
            note = 'bạn chỉ có thể xem thông tin của bản thân'
        #

        if total_users == 0:
            return {
                'users': {},
            }
        pagination_info = calculate_pagination(total_users, page, per_page)

        if users:
            data = {
                'users': users_json,
                'note': note,
                'current_record': len(users_json),
                'current_page': page,
                'total_users': total_users,
                **pagination_info,
                "elapsed_time": elapsed_time

            }
            r.set(key_list_users, json.dumps(data))

            return data

        else:
            return jsonify({"message": "Invalid pagination parameters!"}), 404


@jwt_required()
class check_permission:
    @staticmethod
    def accessible_list(current_user):

        # Đây là danh sách ID mà chúng ta sẽ trả về
        accessible_user_ids = []

        if current_user['role'] == ROLE.ADMIN:
            # Nếu vai trò là admin, trả về danh sách toàn bộ ID của User
            accessible_user_ids = [user.id for user in User.select(User.id)]
        elif current_user['role'] == ROLE.MANAGER:
            # Nếu vai trò là manager, trả về danh sách ID của leader và user thuộc team của manager
            teams = Team.select().where(Team.manager == current_user['id'])
            team_member_ids = (
                TeamMember.select(TeamMember.user_id)
                .where(TeamMember.team_id << teams)
            )
            accessible_user_ids = [tm.user_id for tm in team_member_ids]
        elif current_user['role'] == ROLE.LEADER:
            # Nếu vai trò là leader, trả về danh sách ID của user thuộc team của leader
            team = Team.get(Team.leader == current_user['id'])
            team_member_ids = (
                TeamMember.select(TeamMember.user_id)
                .where((TeamMember.team == team) & (TeamMember.role_id != ROLE.LEADER))
            )
            accessible_user_ids = [tm.user_id for tm in team_member_ids]
        elif current_user['role'] == ROLE.MANAGER:
            # Nếu vai trò là user, trả về ID của user đó
            accessible_user_ids = [current_user['id']]

        return accessible_user_ids


class Get_user_by_id:
    @staticmethod
    def get_user_by_id(user_id):
        current_user = get_jwt_identity()
        accessible_ids = check_permission.accessible_list(current_user)
        if user_id in accessible_ids:
            cache_key = f"user_{user_id}_{current_user['username']}"
            cached_data = r.get(cache_key)
            if cached_data:
                return jsonify({"user": json.loads(cached_data), "source": "Redis Cache"})

            users_data = User.get_or_none(User.id == user_id)

            user_schema = UserSchema()
            user_json = user_schema.dump(users_data)

            r.set(cache_key, json.dumps(user_json))
            return jsonify({"": user_json, "source": "Data Source"})

        else:
            return jsonify({"message": "Not found User or you do not have permission"}, 404)


class Update_user:
    @staticmethod
    def update_user_by_id(user_id):
        current_user = get_jwt_identity()
        accessible_ids = check_permission.accessible_list(current_user)

        if user_id in accessible_ids:
            user_data = User.get_or_none(User.id == user_id)

            data = request.get_json()
            password = data.get('password')

            if 'id' in data or 'username' in data or 'created_at' in data:
                return jsonify({'error': 'Cannot update ID, username, or created_at'}), 400
            try:
                UserSchemaValidate().load(data)
            except ValidationError as e:
                return jsonify({"message": "Invalid input data", "errors": e.messages}), 400

            if current_user['role'] != ROLE.ADMIN and 'role' in data:
                return jsonify({'error': 'Only admin can update the role'}), 403

            if (user_data.id == current_user['id'] or current_user['role'] == ROLE.ADMIN) and 'password' in data:
                hashed_password_result = hash_password(password)
                data['password'] = hashed_password_result
            else:
                return jsonify({'error': 'Can not update the password'}), 403

            data_update = {"id": user_id,
                           "updated_by": current_user['name']
                           }
            data_update.update(data)

            KafkaProducer().send_message("update_user", data_update)
        else:
            return jsonify({"message": "Not found User or you do not have permission"}, 404)
        return 'user are updated'


class Delete_user:
    @staticmethod
    def delete_user_by_id(user_id):
        current_user = get_jwt_identity()
        accessible_ids = check_permission.accessible_list(current_user)

        if user_id in accessible_ids:
            user_data = User.get_or_none(User.id == user_id)

            # Xóa user
            user_data.delete_instance()
            Delete_redis_keys_with_prefix('users')
            Delete_redis_keys_with_prefix(f"user_{user_id}")
            db.commit()
            return jsonify({'message': 'User Deleted !'})

        return jsonify({"message": "Not found User or you do not have permission"}, 404)
