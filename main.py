from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from user_mgmt.authenticate.services import authens
from user_mgmt.User.services import users
from user_mgmt.Team.services import teams


def create_app():
    app = Flask(__name__)
    app.register_blueprint(authens)
    app.register_blueprint(users)
    app.register_blueprint(teams)

    app.json_sort_keys = False  # Để đảm bảo rằng khóa JSON không được sắp xếp
    app.config['JWT_SECRET_KEY'] = 'dlwlrma'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)  # Thời gian tồn tại của access token, ví dụ 30 phút
    jwt = JWTManager(app)  # Khởi tạo JWTManager sau khi tạo app

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
