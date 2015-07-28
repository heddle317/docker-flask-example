import logging

from app import config

from flask import Flask

from flask.ext.compress import Compress
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect


app = Flask(__name__,
            template_folder=config.TEMPLATE_FOLDER,
            static_folder=config.STATIC_FOLDER)
app.config.from_object(config)
Compress(app)
db = SQLAlchemy(app)
csrf = CsrfProtect(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = None
login_manager.init_app(app)

from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('{}/application.log'.format(config.LOG_PATH), 'a', 1 * 1024 * 1024, 10)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)


from app import assets  # NOQA
