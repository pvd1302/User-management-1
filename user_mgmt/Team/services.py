from flask import Blueprint
from user_mgmt.Team.controller import *

teams = Blueprint("teams", __name__)


@teams.route("/team-management/teams", methods=['POST'])
@jwt_required()
def create_team():
    return Create_team.create_team()


@teams.route("/team-management/add-user", methods=['POST'])
@jwt_required()
def add_user_to_team():
    return Add_member.add_user_to_team()


@teams.route("/team-management/teams/<int:id>", methods=['PUT'])
@jwt_required()
def update_team(id: int):
    return Update_team.update_team_by_id(id)


@teams.route("/team-management/teams/<int:id>", methods=['GET'])
@jwt_required()
def get_team(id: int):
    return Get_team.get_team_by_id(id)


@teams.route("/team-management/teams", methods=['GET'])
@jwt_required()
def get_all_teams():
    return View_all_team.get_all_team()


@teams.route("/team-management/teams/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_team(id: int):
    return Delete_team.delete_team_by_id(id)


@teams.route("/team-management/delete-team-member", methods=['POST'])
@jwt_required()
def delete_team_mem():
    return Delete_team_member.delete_team_member()
