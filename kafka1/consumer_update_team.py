import datetime

from confluent_kafka import Consumer
from flask import json
import redis
from library.delete_redis import Delete_redis_keys_with_prefix

from db.model import *

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cấu hình consumer
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_update_team',
    'auto.offset.reset': 'earliest'
}

# Khởi tạo consumer
consumer = Consumer(config)

topic_name = 'update_team'
consumer.subscribe([topic_name])


def update_team():
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        else:
            data_receive = (msg.value()).decode()
            print("update_team: data received: {}".format(data_receive))
            data = json.loads(data_receive)
            team_data = Team.get(Team.id == data['id'])
            updated_at = datetime.datetime.now()
            updated_by = data['updated_by']
            created_by = data['updated_by']
            # create_by = data['updated_by']
            # create_by = data['updated_by']
            if team_data:
                for field, value in data.items():
                    setattr(team_data, field, value)
                team_data.updated_at = updated_at
                team_data.updated_by = updated_by
                # team_data.updated_by = data['updated_by']
            if 'leader_id' in data:
                # Kiểm tra xem đã tồn tại bản ghi của leader hay chưa
                create_leader_data = TeamMember.get_or_none((TeamMember.role == 3) & (TeamMember.team == data['id']))

                if not create_leader_data:
                    # Nếu không tồn tại, tạo mới bản ghi leader
                    create_leader_data = TeamMember.create(user=data['leader_id'], team=data['id'], role=3,
                                                           created_by=updated_by, updated_by=updated_by,
                                                           updated_at=updated_at)
                    create_leader_data.save()

                else:
                    # nếu đã có thì update
                    leader_data = TeamMember.get_or_none((TeamMember.role == 3) & (TeamMember.team == data['id']))
                    leader_data.user = data['leader_id']
                    leader_data.updated_at = updated_at
                    leader_data.updated_by = updated_by
                    leader_data.update()
                    leader_data.save()
                print('Received message: {}'.format(msg.value()))
            if 'manager_id' in data:

                # Kiểm tra xem đã tồn tại bản ghi của manager hay chưa
                create_manager_data = TeamMember.get_or_none((TeamMember.role == 2) & (TeamMember.team == data['id']))
                if not create_manager_data:
                    # Nếu không tồn tại, tạo mới bản ghi manager
                    create_manager_data = TeamMember.create(user=data['manager_id'], team=data['id'], role=2,
                                                            created_by=updated_by, updated_by=updated_by,
                                                            updated_at=updated_at)
                    create_manager_data.save()

                else:
                    # nếu đã có thì update
                    manager_data = TeamMember.get((TeamMember.role == 2) & (TeamMember.team == data['id']))
                    if manager_data:
                        manager_data.user = data['manager_id']
                        manager_data.updated_at = datetime.datetime.now()
                        manager_data.updated_by = data['updated_by']
                        manager_data.save()
            team_data.save()
            Delete_redis_keys_with_prefix(f"team_{data['id']}")
            Delete_redis_keys_with_prefix(f'users')


if __name__ == "__main__":
    update_team()
