from flask import Blueprint
from user_mgmt.User.controller import *

users = Blueprint("users", __name__)


@users.route("/user-management/users", methods=['GET'])
@jwt_required()
def get_user():
    return Get_user.get_all_user_service()


@users.route("/user-management/users/<int:id>", methods=['GET'])
@jwt_required()
def get_user_by_id(id: int):
    return Get_user_by_id.get_user_by_id(id)


@users.route("/user-management/users/<int:id>", methods=['PUT'])
@jwt_required()
def update_user(id: int):
    return Update_user.update_user_by_id(id)


@users.route("/user-management/users/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_user(id: int):
    return Delete_user.delete_user_by_id(id)
