import logging
import logging.config
from os import name

from flask import Flask, render_template, session, Response, request
from flask_socketio import SocketIO, emit

import base64
import time
import json

from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_ns import SuricateCmdNS
from watcher_debug_ns import WatcherDebugNS
from watcher_cmd_ns import WatcherCmdNS
from watcher_video_cast_ns import WatcherVideoCastNS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

logging.config.fileConfig('logger.conf', disable_existing_loggers=False)
my_logger = logging.getLogger('suricate_server')
my_logger.info('Logger init done')

socketio = SocketIO(app, logger = True)

connection_count = 0
toto = 0
img = ''

class Suricate:
	def __init__(self, id) -> None:
		
		self.id = id
		self.sid_cmd = '-------'
		self.sid_stream = '-------'


class Server:
	def __init__(self):
		self._suricate_count = 0
		self._watchers_count = 0
		self._suricate_sid = 'NOT_SET'
		self._suricates = {}
		self._suricate_rooms = {}

		self._suricates['AZE'] = Suricate('AZE')
		self._suricates['QSD'] = Suricate('QSD')
		
		socketio.on_namespace(WatcherDebugNS('/debug', suricate_server=self))
		socketio.on_namespace(SuricateVideoStreamNS('/suricate_video_stream', suricate_server=self))
		socketio.on_namespace(SuricateCmdNS('/suricate_cmd', suricate_server=self))
		socketio.on_namespace(WatcherVideoCastNS('/watcher_video_cast', suricate_server=self))
		socketio.on_namespace(WatcherCmdNS('/watcher_cmd', suricate_server=self))
	

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
	
	def create_room(self, sid, name):

		self._suricate_rooms[sid] = name

	def register_suricate(self, id):

		suricate = Suricate(id)
		suricate.sid_cmd = request.sid
		self._suricates[id] = suricate

	def suricate_id(self, sid):
		''' return index of suricate with sid_cmd == sid in _suricates dict '''

		# get index of suricate with sid_cmd == sid in _suricates dict '''
		id = [ x.sid_cmd for x in list(self._suricates.values()) ].index(sid)

		return self._suricates[id]

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


my_server = Server()


@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode, connection_count=connection_count, suricate_server=my_server)

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
	