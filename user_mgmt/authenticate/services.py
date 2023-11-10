from flask import Blueprint
from user_mgmt.authenticate.controller import *

authens = Blueprint("authens", __name__)


@authens.route("/users-management/register", methods=['POST'])
def register():
    return register_service()


@authens.route("/users-management/login", methods=['POST'])
def login():
    return login_service()

