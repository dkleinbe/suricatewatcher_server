from typing import List
import coloredlogs, logging
import logging.config
from os import name
from typing import NewType, Optional

from flask import Flask, render_template, session, Response, request 
from flask_socketio import SocketIO, emit, join_room, leave_room

import base64
import time
import json

from my_types import SessionId
from suricate import Suricate
from watcher import Watcher
from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_ns import SuricateCmdNS
from watcher_debug_ns import WatcherDebugNS
from watcher_cmd_ns import WatcherCmdNS
from watcher_video_cast_ns import WatcherVideoCastNS



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

with open('logger_conf2.json') as json_file:
    conf = json.load(json_file)
logging.config.dictConfig(conf['logging'])

my_logger = logging.getLogger('suricate_server')

my_logger.debug('Logger debug')
my_logger.info('Logger init done')
my_logger.warning('Logger warning')
my_logger.error('Logger error')
my_logger.critical('Logger critical')

socketio = SocketIO(app) #, logger = my_logger)


connection_count = 0

class Server:
	def __init__(self):
		self._suricate_count : int = 0
		self._watchers_count : int = 0
		self._suricates: dict[SessionId, Suricate] = {}
		self._watchers : dict[SessionId, Watcher] = {}
		
		
		socketio.on_namespace(WatcherDebugNS('/debug', suricate_server=self))
		socketio.on_namespace(SuricateVideoStreamNS('/suricate_video_stream', suricate_server=self))
		socketio.on_namespace(SuricateCmdNS('/suricate_cmd', suricate_server=self))
		socketio.on_namespace(WatcherVideoCastNS('/watcher_video_cast', suricate_server=self))
		socketio.on_namespace(WatcherCmdNS('/watcher_cmd', suricate_server=self))

	def register_watcher(self, sid : SessionId):

		watcher = Watcher(id=sid, suricate_server=self)
		self._watchers[sid] = watcher

	def unregister_watcher(self, id : SessionId) -> None:

		self._watchers[id].stop_watching()
		del self._watchers[id]

	def register_suricate(self, sid : SessionId):

		suricate = Suricate(sid)
		#suricate.sid_cmd = request.sid
		self._suricates[sid] = suricate

	def unregister_suricate(self, id : SessionId):

		del self._suricates[id]

	def suricate_id(self, sid : SessionId) -> Suricate:
		''' return Suricate with sid_cmd == sid in _suricates dict '''

		# get index of suricate with sid_cmd == sid in _suricates dict '''
		index = [ x.suricate_cmd_sid for x in list(self._suricates.values()) ].index(sid)

		return list(self._suricates.values())[index]	

	@property
	def suricate_count(self):
		my_logger.debug('+ Getting suricate_count: ' + str(self._suricate_count))
		return self._suricate_count

	@suricate_count.setter
	def suricate_count(self, count):
		my_logger.debug('+ Setting suricate_count: ' + str(count))
		self._suricate_count = count

	@property
	def watchers_count(self):
		my_logger.debug('+ Getting watchers_count: ' + str(self._watchers_count))
		return self._watchers_count

	@watchers_count.setter
	def watchers_count(self, count : int):
		my_logger.debug('+ Setting watchers_count: ' + str(count))
		self._watchers_count = count
	
	def toJSON(self):
		# FIXME : Deal with circular reference
		#return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
		return "TO FIXE"
		
		

my_server = Server()

 
@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode, connection_count=connection_count, suricate_server=my_server)

@app.route('/joystick')
def joystick():
	return render_template('dual-joysticks.html', async_mode=socketio.async_mode, suricate_server=my_server)

@app.route('/debug')
def debug():
	return render_template('debug.html', async_mode=socketio.async_mode, suricate_server=my_server)


if __name__ != '__main__':
    #gunicorn_logger = logging.getLogger('gunicorn.error')
    #app.logger.handlers = gunicorn_logger.handlers
    #app.logger.setLevel(gunicorn_logger.level)
	my_logger.info("STARTING SERVER")

if __name__ == '__main__':

	app.logger.info("Launching server...")
	
	socketio.run(app, host="0.0.0.0", debug=False)
	