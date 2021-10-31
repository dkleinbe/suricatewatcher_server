from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import json
from .suricate_server import Server

from config import Config

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
server = None
socketio = None

import logging.config
import coloredlogs, logging

with open('./server/logger_conf2.json') as json_file:
	conf = json.load(json_file)
logging.config.dictConfig(conf['logging'])

my_logger = logging.getLogger(__name__)

my_logger.debug('Logger debug')
my_logger.info('Logger info')
my_logger.warning('Logger warning')
my_logger.error('Logger error')
my_logger.critical('Logger critical')

def create_app():
	app = Flask(__name__)
	app.config.from_object("config.Config")

	global socketio, my_logger
	socketio = SocketIO() # logger = my_logger

	global server
	server = Server(socketio)

	db.init_app(app)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login' # type: ignore
	login_manager.init_app(app)

	from .models import User

	@login_manager.user_loader
	def load_user(user_id):
		# since the user_id is just the primary key of our user table, use it in the query for the user
		return User.query.get(int(user_id))

	# blueprint for auth routes in our app
	from .auth.auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	# blueprint for non-auth parts of app
	from .main.main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	socketio.init_app(app)

	return app, socketio





