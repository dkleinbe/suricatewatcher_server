import logging
import logging.config
from os import name

from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit
from watcher_video_cast_ns import WatcherVideoCastNS
from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_suricate_ns import SuricateCmdSuricateNS
from watcher_debug_ns import WatcherDebugNS
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
		self._suricate_count = 0
		self._watchers_count = 0
		self._suricate_sid = 'NOT_SET'

		socketio.on_namespace(WatcherDebugNS('/debug', suricate_server=self))
		socketio.on_namespace(SuricateVideoStreamNS('/suricate_video_stream'))
		socketio.on_namespace(SuricateCmdSuricateNS('/suricate_cmd', suricate_server=self))
		socketio.on_namespace(WatcherVideoCastNS('/watcher_video_cast', suricate_server=self))
	
	@property
	def suricate_sid(self):
		my_logger.info('+ Getting suricate sid: ' + str(self._suricate_sid))
		return self._suricate_sid
	
	@suricate_sid.setter
	def suricate_sid(self, sid):
		my_logger.info('+ Setting suricate sid: ' + str(sid))
		self._suricate_sid = sid

	@property
	def suricate_count(self):
		my_logger.info('+ Getting suricate_count: ' + str(self._suricate_count))
		return self._suricate_count

	@suricate_count.setter
	def suricate_count(self, count):
		my_logger.info('+ Setting suricate_count: ' + str(count))
		self._suricate_count = count

	@property
	def watchers_count(self):
		my_logger.info('+ Getting watchers_count: ' + str(self._watchers_count))
		return self._watchers_count

	@watchers_count.setter
	def watchers_count(self, count):
		my_logger.info('+ Setting watchers_count: ' + str(count))
		self._watchers_count = count
	
	
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


my_server = Server()


@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode, connection_count=connection_count)

@app.route('/debug')
def debug():
	return render_template('debug.html', async_mode=socketio.async_mode, suricate_server=my_server)


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
	