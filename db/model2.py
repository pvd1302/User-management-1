# from peewee import *
#
# db = PostgresqlDatabase('User_mgmt', host='localhost', port=5432, user='postgres', password='postgres')
#
#
# class Role(Model):
#     name = CharField(unique=True)
#
#     class Meta:
#         database = db
#
#
# # Định nghĩa mô hình cho Team
# class Team(Model):
#     name = CharField()
#
#     class Meta:
#         database = db
#
#
# # Định nghĩa mô hình cho User
# class User(Model):
#     username = CharField(unique=True)
#     role = ForeignKeyField(Role)
#     teams = ForeignKeyField(Team, null=True)
#
#     class Meta:
#         database = db
#
#
# # Định nghĩa mô hình cho TeamMember
# class TeamMember(Model):
#     user = ForeignKeyField(User)
#     team = ForeignKeyField(Team)
#     role = ForeignKeyField(Role)
#
#     class Meta:
#         database = db
#
#
# if __name__ == '__main__':
#     # Tạo bảng trong cơ sở dữ liệu
#     db.connect()
#     db.create_tables([Role, Team, User, TeamMember])
#
#     # Tạo các vai trò "admin", "manager", và "user"
#     admin_role = Role.create(name='admin')
#     manager_role = Role.create(name='manager')
#     user_role = Role.create(name='user')
#
#     # Tạo các nhóm
#     team1 = Team.create(name='Team 1')
#     team2 = Team.create(name='Team 2')
#
#     # Tạo người dùng "admin123" với vai trò "admin"
#     admin_user = User.create(username='admin123', role=admin_role)
#
#     # Tạo người dùng "manager456" với vai trò "manager" và gán vào "Team 1"
#     manager_user = User.create(username='manager456', role=manager_role, teams=team1)
#
#     # Tạo người dùng "user789" với vai trò "user" và gán vào "Team 2"
#     user_user = User.create(username='user789', role=user_role, teams=team2)
#
#     # Gán người dùng "user789" làm leader của "Team 1"
#     leader_role = Role.create(name='leader')
#     TeamMember.create(user=user_user, team=team1, role=leader_role)
