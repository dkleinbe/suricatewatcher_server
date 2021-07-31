from typing import List
import logging
import logging.config
from os import name
from typing import NewType, Optional

from flask import Flask, render_template, session, Response, request 
from flask_socketio import SocketIO, emit, join_room, leave_room

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

SessionId = NewType('SessionId', str)

class Watcher:
	def __init__(self, id : SessionId):

		self.id : SessionId = id
		
		self.watcher_cmd_sid        : SessionId = SessionId('NONE')
		self.watcher_video_cast_sid : SessionId = SessionId('NONE')
		self.watched_suricate_id    : SessionId = SessionId('NONE')
		self.watched_suricate       : Optional[Suricate] = None

		
	def watch_suricate(self, watcher_video_cast_sid : SessionId, suricate_sid : SessionId) -> None:

		# if we are already watching a suricate, stop watching
		if (self.watched_suricate != None) :
			
			self.stop_watching()

		# Stop watching
		if (suricate_sid == 'NONE'):
			return

		self.watcher_video_cast_sid = watcher_video_cast_sid
		suricate = my_server._suricates[suricate_sid]
		suricate.add_watcher(self.watcher_video_cast_sid)
		self.watched_suricate = suricate
	
	def stop_watching(self) -> None :

		if (self.watched_suricate != None):
			self.watched_suricate.remove_watcher(self.watcher_video_cast_sid)
		self.watched_suricate = None

class Suricate:
	""" init a Suricat.

		:param sid: The session id of the suricate_cmd namespace.

	"""
	def __init__(self, sid : SessionId) -> None:

		self.room                      : str = 'room_' + sid # create room name from sid
		self.suricate_cmd_sid          : SessionId = sid
		self.suricate_video_stream_sid : SessionId = SessionId('NONE')
		self.watchers                  : List[SessionId] = []

	def add_watcher(self, watcher_sid : SessionId):
		#
		# add watcher to suricat room
		#
		my_logger.info('+ Entering room [%s]', self.room)
		join_room(sid=watcher_sid, room=self.room, namespace='/watcher_video_cast')

		# add watcher to watcher list
		self.watchers.append(watcher_sid)

		#
		# start suricate video stream
		#
		my_logger.info("+ starting suricate stream: %s", self.suricate_cmd_sid)
		emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def remove_watcher(self, watcher_sid : SessionId):
		
		# lets leave the room
		my_logger.debug('+ removing watcher from room <%s>', self.room)
		leave_room(sid=watcher_sid, room=self.room, namespace='/watcher_video_cast')

		# remove watcher from watcher list
		self.watchers.remove(watcher_sid)
		
		if (len(self.watchers) <= 0):
			# if no more watcher for this suricate stop video stream
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

class Server:
	def __init__(self):
		self._suricate_count : int = 0
		self._watchers_count : int = 0
		self._suricates: dict[SessionId, Suricate] = {}
		self._suricate_rooms = {}
		self._watchers : dict[SessionId, Watcher] = {}
		
		
		socketio.on_namespace(WatcherDebugNS('/debug', suricate_server=self))
		socketio.on_namespace(SuricateVideoStreamNS('/suricate_video_stream', suricate_server=self))
		socketio.on_namespace(SuricateCmdNS('/suricate_cmd', suricate_server=self))
		socketio.on_namespace(WatcherVideoCastNS('/watcher_video_cast', suricate_server=self))
		socketio.on_namespace(WatcherCmdNS('/watcher_cmd', suricate_server=self))
	
	def create_room(self, sid, name):

		self._suricate_rooms[sid] = name

	def register_watcher(self, id : SessionId):

		watcher = Watcher(id)
		self._watchers[id] = watcher

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
	def watchers_count(self, count : int):
		my_logger.info('+ Setting watchers_count: ' + str(count))
		self._watchers_count = count
	
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
	