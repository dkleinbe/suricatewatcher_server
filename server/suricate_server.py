import logging
import logging.config
from os import name

from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit
from watcher_video_cast_ns import WatcherVideoCastNS
from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_suricate_ns import SuricateCmdSuricateNS
import base64
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

logging.config.fileConfig('logger.conf', disable_existing_loggers=False)
my_logger = logging.getLogger('suricate_server')
my_logger.info('Logger init done')

socketio = SocketIO(app, logger = True)

connection_count = 0
toto = 0
img = ''

class Server:
	def __init__(self):
		self._nb_watchers = 0
		self._suricate_sid = 'NOT_SET'

		socketio.on_namespace(SuricateVideoStreamNS('/video_stream'))
		socketio.on_namespace(SuricateCmdSuricateNS('/cmd_suricate', suricate_server=self))
		socketio.on_namespace(WatcherVideoCastNS('/video_cast', suricate_server=self))
	
	@property
	def suricate_sid(self):
		my_logger.info('+ Getting suricate sid: ' + str(self._suricate_sid))
		return self._suricate_sid
	
	@suricate_sid.setter
	def suricate_sid(self, sid):
		my_logger.info('+ Setting suricate sid: ' + str(sid))
		self._suricate_sid = sid
		
	@property
	def nb_watchers(self):
		my_logger.info('+ Getting nb_watchers: ' + str(self._nb_watchers))
		return self._nb_watchers

	@nb_watchers.setter
	def nb_watchers(self, count):
		my_logger.info('+ Setting nb_watchers: ' + str(count))
		self._nb_watchers = count
	
	def dummy(self):
		return 'TOTO: ' + str(self._nb_watchers)
	
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


my_server = Server()


@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode, connection_count=connection_count)

@app.route('/debug')
def debug():
	return render_template('debug.html', async_mode=socketio.async_mode, suricate_server=my_server)

@socketio.on('connect', namespace='/debug')
def on_connect():
	#app.logger.info("+ /debug: connect")
	pass


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':

	#logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
	logging.getLogger('suricate_server').setLevel(logging.DEBUG)
	
	#logging.getLogger('socketio').setLevel(logging.ERROR)
	#logging.getLogger('engineio').setLevel(logging.ERROR)

	app.logger.info("Launching server...")
	
	socketio.run(app, host="0.0.0.0", debug=False)
	