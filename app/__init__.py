import logging
import os
from typing import Optional

from flask import Flask
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
DEBUG_MODE = os.getenv('debug')

DB_NAME = os.getenv('db_name')
ADMIN_ROLE_NAME = 'admin'
DEFAULT_ADMIN_LOGIN = 'admin'
logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO)

db = SQLAlchemy()
auth = HTTPBasicAuth()


def fill_default_database(flask_app: Flask):
    from app.models import Role, User

    with flask_app.app_context():
        db.create_all()

        admin_role = Role.query.filter_by(name=ADMIN_ROLE_NAME).scalar()

        if not admin_role:
            admin_role = Role(name=ADMIN_ROLE_NAME)
            db.session.add(admin_role)
            db.session.commit()

        default_user = User.query.filter_by(login=DEFAULT_ADMIN_LOGIN).scalar()

        if not default_user:
            default_user = User(
                login=DEFAULT_ADMIN_LOGIN,
                password=generate_password_hash(os.getenv('default_admin_password')),
            )

            default_user.roles.append(admin_role)

            db.session.add(default_user)
            db.session.commit()


@auth.verify_password
def verify_password(username, password):
    from app.models import User
    user = User.query.filter_by(login=username).scalar()

    if not user:
        return None

    return check_password_hash(user.password, password)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    fill_default_database(app)
    return app
