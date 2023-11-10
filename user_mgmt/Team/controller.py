from flask import request, jsonify, json
from flask_jwt_extended import get_jwt_identity, jwt_required
from peewee import *
from playhouse.shortcuts import model_to_dict
from db.model import *
from flask import request, jsonify, json
import redis
from db.mash import UserSchema
from marshmallow import ValidationError
import datetime

from library.validate import UserSchemaValidate
from library.delete_redis import Delete_redis_keys_with_prefix
from library.find_name import apply_team_name_condition
from library.constant import ROLE
from library.pagination import calculate_pagination

from kafka1.producer import KafkaProducer

r = redis.StrictRedis(host='localhost', port=6379, db=0)

producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'client_teams'
}


@jwt_required()
class check_permission:
    @staticmethod
    def accessible_list(current_user):
        # current_user = get_jwt_identity()

        accessible_teams = []

        if current_user['role'] == ROLE.ADMIN:
            teams = Team.select()
            accessible_teams = [tm.id for tm in teams]
        elif current_user['role'] == ROLE.MANAGER:
            teams = Team.select().where(Team.manager == current_user['id'])
            accessible_teams = [tm.id for tm in teams]

        elif current_user['role'] == ROLE.LEADER:
            teams = Team.select().where(Team.leader == current_user['id'])
            accessible_teams = [tm.id for tm in teams]

        elif current_user['role'] == ROLE.MEMBER:
            teams = Team.select().where(Team.id < 0)  # Trả về danh sách rỗng
            accessible_teams = [tm.id for tm in teams]

        return accessible_teams


class Create_team:
    @staticmethod
    def create_team():
        current_user = get_jwt_identity()
        if current_user['role'] == 1:
            data = request.get_json()
            name = data.get('name')
            leader_id = data.get('leader_id')
            manager_id = data.get('manager_id')
            updated_at = datetime.datetime.now()
            created_by = current_user['name']
            updated_by = current_user['name']

            # Kiểm tra xem leader và manager có tồn tại và có đúng role hay không
            leader = User.get_or_none((User.id == leader_id) & (User.role == ROLE.LEADER))
            manager = User.get_or_none((User.id == manager_id) & (User.role == ROLE.MANAGER))

            if leader is None or manager is None:
                return jsonify({"message": "Leader and Manager must have the correct roles"}), 400

            # Tạo một nhóm mới với leader và manager đã chọn
            new_team = Team.create(name=name, leader=leader, manager=manager,
                                   created_by=created_by, updated_at=updated_at, updated_by=updated_by)
            new_team.save()

            # Tạo bản ghi trong bảng TeamMember
            TeamMember.create(user=leader, team=new_team.id, role=ROLE.MANAGER,
                              created_by=created_by, updated_at=updated_at, updated_by=updated_by)
            TeamMember.create(user=manager, team=new_team.id, role=ROLE.LEADER,
                              created_by=created_by, updated_at=updated_at, updated_by=updated_by)

            return jsonify({"message": "Team created successfully"}), 201
        else:
            return jsonify({"message": "You don't have enough permission !"}), 404


class Add_member:
    @staticmethod
    def add_user_to_team():
        current_user = get_jwt_identity()
        data = request.get_json()
        team_id = data.get('team_id')
        user_id = data.get('user_id')
        updated_at = datetime.datetime.now()
        created_by = current_user['name']
        updated_by = current_user['name']

        accessible_teams = check_permission.accessible_list(current_user)
        if team_id in accessible_teams:
            existing_record = TeamMember.get_or_none(
                (TeamMember.user == user_id) & (TeamMember.team == team_id))

            if existing_record:
                # Nếu bản ghi tồn tại, thông báo rằng người dùng đã trong team này rồi
                return jsonify({"message": f"User is already in this team"}), 400
            user_to_add = User.get_or_none(User.id == user_id)
            if user_to_add is None:
                return jsonify({"message": "User not found"}), 404

            elif user_to_add:
                # Tạo một bản ghi TeamMember với vai trò mặc định là 4
                TeamMember.create(user=user_to_add, team=team_id, role=ROLE.MEMBER,
                                  created_by=created_by, updated_at=updated_at, updated_by=updated_by)

            Delete_redis_keys_with_prefix(f"team_{team_id}")
            Delete_redis_keys_with_prefix(f'users')
        else:
            return jsonify({"message": "You do not have permission or Team's ID doesn't exist"}, 404)

        return jsonify({"message": "User added to team successfully"}), 201


class Update_team:
    @staticmethod
    def update_team_by_id(team_id):
        current_user = get_jwt_identity()
        accessible_teams = check_permission.accessible_list(current_user)
        print(accessible_teams)
        if team_id in accessible_teams:
            data = request.get_json()

            if 'manager_id' in data and current_user['role'] == ROLE.ADMIN:
                manager = User.get_or_none(User.id == data['manager_id'])
                if manager is None:
                    return jsonify({'message': 'manager ID does not exist!'})
                if manager.role.id != ROLE.MANAGER:
                    return jsonify({'message': "User's IU is not a manager"})
            elif 'manager_id' in data and current_user['role'] == ROLE.ADMIN:

                return jsonify({'message': 'You do not have permission'})

            if 'leader_id' in data and current_user['role'] in [ROLE.ADMIN, ROLE.MANAGER]:
                leader = User.get_or_none(User.id == data['leader_id'])
                if leader is None:
                    return jsonify({'message': 'Leader ID does not exist!'})
                if leader.role.id != 3:
                    return jsonify({'message': "User's IU is not a leader"})

            elif 'leader_id' in data and current_user['role'] in [ROLE.LEADER, ROLE.MEMBER]:
                return jsonify({'message': 'You do not have permission'})

            data_update = {"id": team_id,
                           "updated_by": current_user['name']
                           }
            data_update.update(data)
            KafkaProducer().send_message("update_team", data_update)

        else:
            return jsonify({"message": "You do not have permission or Team's ID doesn't exist"}, 404)

        return jsonify({'message': 'Team Updated !'})


class Get_team:
    @staticmethod
    def get_team_by_id(team_id):
        current_user = get_jwt_identity()
        team_data = Team.get_or_none(Team.id == team_id)
        accessible_teams = check_permission.accessible_list(current_user)
        if team_data and team_data.id in accessible_teams:
            cache_key = f"team_{team_id}_{current_user['id']}"
            cached_data = r.get(cache_key)
            if cached_data:
                return jsonify({"team": json.loads(cached_data), "source": "Redis Cache"})

            manager = team_data.manager
            leader = team_data.leader
            team_members = TeamMember.select().where(TeamMember.team == team_data)
            team_member_list = [{"user id": member.user.id, "user name": member.user.name} for member in
                                team_members]

            team_info = {
                "1.team_id": team_data.id,
                "2.team_name": team_data.name,
                "3.manager_name": manager.name if manager else None,
                "4.leader_name": leader.name if leader else None,
                "5.team_members": team_member_list
            }

            r.set(cache_key, json.dumps(team_info))
        else:
            return jsonify({"message": "Not found Teams !"}, 404)
        return jsonify({'': team_info, "source": "Data Source"}), 200


class View_all_team:
    @staticmethod
    def get_all_team():
        teams_data = []

        # truyền vào thông số phân trang
        page = int(request.args.get('page'))
        if page < 1:
            return jsonify({'message': 'Invalid pagination parameters. Page must be greater than or equal to 1'})
        per_page = int(request.args.get('per_page'))

        # tìm kiếm theo tên
        name_team = request.args.get('name')

        current_user = get_jwt_identity()

        if name_team:
            key_list_users = f"teams_{current_user['username']}_{page}_{per_page}_{name_team}"
        else:
            key_list_users = f"teams_{current_user['username']}_{page}_{per_page}"

        cached_data = r.get(key_list_users)
        if cached_data:
            return jsonify(json.loads(cached_data))

        if current_user :
            teams_query = Team.select().order_by(Team.id)
            teams_query = apply_team_name_condition(teams_query, name_team)

            total_teams = teams_query.count()
            teams = teams_query.order_by(Team.id).limit(per_page).offset((per_page * page) - per_page)
            note = 'bạn có thể xem toàn bộ danh sách'
            for t in teams:
                team_dict = model_to_dict(t, exclude=[Team.leader, Team.manager, Team.updated_by, Team.updated_at,
                                                      Team.created_by, Team.created_at])

                teams_data.append(team_dict)

            if total_teams == 0:
                return {
                    'users': {},
                }

            # Tính toán phân trang
            pagination_info = calculate_pagination(total_teams, page, per_page)

            if teams_data:
                data = {
                    'teams': teams_data,
                    'note': note,
                    'current_record': len(teams_data),
                    'current_page': page,
                    'total_users': total_teams,
                    **pagination_info
                }
                r.set(key_list_users, json.dumps(data))

                return data

            else:
                return jsonify({"message": "Invalid pagination parameters!"}), 404

class Delete_team:
    @staticmethod
    def delete_team_by_id(team_id):
        current_user = get_jwt_identity()
        # team_data = Team.get_or_none(Team.id == team_id)
        accessible_teams = check_permission.accessible_list(current_user)
        if team_id in accessible_teams:
            team_member = TeamMember.get(TeamMember.team == team_id)
            TeamMember.delete_by_id(team_member.id)
            Team.delete_by_id(team_id)
            Delete_redis_keys_with_prefix(f"team_{team_id}")
            Delete_redis_keys_with_prefix(f"users")
            db.commit()

        else:
            return jsonify({'message': "Team doesn't exist !"})
        return jsonify({'message': 'Team Deleted !'})


class Delete_team_member:
    @staticmethod
    def delete_team_member():
        data = request.get_json()
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        current_user = get_jwt_identity()
        accessible_teams = check_permission.accessible_list(current_user)
        # team_data = Team.get_or_none(Team.id == team_id)

        if team_id in accessible_teams:
            team_member = TeamMember.get((TeamMember.user == user_id) & (TeamMember.team == team_id))
            if team_member.role == ROLE.MANAGER or team_member.role == ROLE.LEADER:
                return jsonify("can not delete manager and leader !!!")
            team_member.delete_instance()
            Delete_redis_keys_with_prefix(f"team_{team_id}")
            Delete_redis_keys_with_prefix(f"users")
            db.commit()

        else:
            return jsonify({'message': 'Team or member not found'}), 404

        return jsonify({'message': 'Team member Deleted !'})
