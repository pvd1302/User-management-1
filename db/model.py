from peewee import *

# Kết nối đến cơ sở dữ liệu PostgreSQL
db = PostgresqlDatabase('user-mng', host='localhost', port=5432, user='postgres', password='postgres')


# Định nghĩa mô hình cho Role, Team, User và TeamMember
class Role(Model):
    id = AutoField()
    name = CharField(unique=True)

    class Meta:
        database = db


class User(Model):
    id = AutoField()
    name = CharField()
    age = IntegerField()
    address = CharField()
    phone_number = CharField()
    email = CharField()
    role = ForeignKeyField(Role)
    username = CharField(unique=True)
    password = CharField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT now()')])
    updated_at = DateTimeField()
    created_by = CharField()
    updated_by = CharField()

    class Meta:
        database = db


class Team(Model):
    id = AutoField()
    name = CharField()
    leader = ForeignKeyField(User, related_name='leading_teams', null=True, on_delete='SET NULL')
    manager = ForeignKeyField(User, related_name='managed_teams', null=True, on_delete='SET NULL')
    created_at = DateTimeField(constraints=[SQL('DEFAULT now()')])
    updated_at = DateTimeField()
    created_by = CharField()
    updated_by = CharField()

    class Meta:
        database = db


class TeamMember(Model):
    id = AutoField()
    user = ForeignKeyField(User, on_delete='CASCADE')
    team = ForeignKeyField(Team, on_delete='CASCADE')
    role = ForeignKeyField(Role)
    created_at = DateTimeField(constraints=[SQL('DEFAULT now()')])
    updated_at = DateTimeField()
    created_by = CharField()
    updated_by = CharField()

    class Meta:
        database = db


if __name__ == '__main__':
    # Tạo bảng trong cơ sở dữ liệu
    db.connect()
    db.create_tables([TeamMember])

    # # Tạo các vai trò "admin", "manager", "user", và "leader"
    # admin_role = Role.create(name='admin')
    # manager_role = Role.create(name='manager')
    # user_role = Role.create(name='user')
    # leader_role = Role.create(name='leader')
    #
    # # Tạo các nhóm
    # team1 = Team.create(name='Team 1')
    # team2 = Team.create(name='Team 2')
    # team3 = Team.create(name='Team 3')
    #
    # # Tạo người dùng "admin123" với vai trò "admin"
    # admin_user = User.create(username='admin123', role=admin_role)
    #
    # # Tạo người quản lý "manager456" với vai trò "manager" và gán vào "Team 1"
    # manager_user = User.create(username='manager456', role=manager_role, teams=team1)
    #
    # # Tạo người dùng "user789" với vai trò "user" và gán vào "Team 2"
    # user_user = User.create(username='user789', role=user_role, teams=team2)
    #
    # # Gán người dùng "user789" làm leader của "Team 3"
    # TeamMember.create(user=user_user, team=team3, role=leader_role)
    #
    # print("Database initialized.")
