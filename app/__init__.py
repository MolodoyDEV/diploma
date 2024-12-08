import logging
import os
import sqlite3

from flask import Flask
from dotenv import load_dotenv

load_dotenv()
DEBUG_MODE = os.getenv('debug')

DB_NAME = os.getenv('db_name')
logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO)


def create_db_connection() -> sqlite3.Connection:
    try:
        con = sqlite3.connect(DB_NAME)
        return con
    except sqlite3.Error as e:
        logging.error(e)
        raise e


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['DEBUG'] = DEBUG_MODE
    return app
