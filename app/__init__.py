import logging
import os
from typing import List, Dict, Any

from deep_translator import GoogleTranslator
from flask import Flask, abort
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils import load_model, load_tokenizer

load_dotenv()
DEBUG_MODE = os.getenv('debug')

DB_NAME = os.getenv('db_name')
ADMIN_ROLE_NAME = 'admin'
DEFAULT_ADMIN_LOGIN = 'admin'

logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO)

db = SQLAlchemy()
auth = HTTPBasicAuth()
translator_to_en = GoogleTranslator(source='auto', target='en')

model_by_name: Dict[str, Dict[str, Any]] = {
    'fishing': {},
    'fraud': {},
    'spam': {},
}

for name in model_by_name.keys():
    model_by_name[name]['model'] = load_model(f'models/{name}')
    model_by_name[name]['tokenizer'] = load_tokenizer(f'tokenizers/{name}')


def fill_default_database(flask_app: Flask):
    from app.models import Role, User, Settings

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

        DEFAULT_SETTINGS = {
            'fishing_threshold': '0.985',
            'fraud_threshold': '0.90',
            'spam_threshold': '0.98',
        }

        for k, v in DEFAULT_SETTINGS.items():
            if not Settings.query.filter_by(name=k).scalar():
                db.session.add(Settings(name=k, value=v))

        db.session.commit()


def create_admin_panel(app: Flask):
    from app.models import Role, User, Settings

    admin = Admin(app, name='mail', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Role, db.session))
    admin.add_view(ModelView(Settings, db.session))

    return admin


@auth.verify_password
def verify_password(username, password):
    from app.models import User
    user = User.query.filter_by(login=username).scalar()

    if not user:
        return None

    return check_password_hash(user.password, password)


@auth.get_user_roles
def get_user_roles(authorization) -> List[str]:
    if not authorization:
        return abort(401)

    from app.models import User

    username = authorization.parameters['username']
    user = User.query.filter_by(login=username).scalar()

    if not user:
        return abort(401)

    return [x.name for x in user.roles]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    fill_default_database(app)
    create_admin_panel(app)
    return app
