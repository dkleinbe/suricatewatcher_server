from collections import deque
from typing import List
from os import name
from typing import NewType, Optional

from flask import Flask, render_template, session, request 
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

import logging
import base64
import time


from .my_types import SessionId
from .watcher import Watcher
from .suricate import Suricate
from .suricate_video_stream_ns import SuricateVideoStreamNS
from .suricate_cmd_ns import SuricateCmdNS
from .watcher_debug_ns import WatcherDebugNS
from .watcher_cmd_ns import WatcherCmdNS
from .watcher_video_cast_ns import WatcherVideoCastNS
from .cam_controller import CamController
from .filters import ButterFilter

logger = logging.getLogger(__name__)

class Server:
	def __init__(self, socketio):

		logger.info("+ Init Server")

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

		watcher = Watcher(watcher_cmd_sid=sid, suricate_server=self)
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
		logger.debug('+ Getting suricate_count: ' + str(self._suricate_count))
		return self._suricate_count

	@suricate_count.setter
	def suricate_count(self, count):
		logger.debug('+ Setting suricate_count: ' + str(count))
		self._suricate_count = count

	@property
	def watchers_count(self):
		logger.debug('+ Getting watchers_count: ' + str(self._watchers_count))
		return self._watchers_count

	@watchers_count.setter
	def watchers_count(self, count : int):
		logger.debug('+ Setting watchers_count: ' + str(count))
		self._watchers_count = count
	
	def toJSON(self):
		return "deprecated"
		#return json.dumps(self, cls=MyEncoder, check_circular=False, indent=2)
		
		
if False:
	if __name__ != '__main__':
		#gunicorn_logger = logging.getLogger('gunicorn.error')
		#app.logger.handlers = gunicorn_logger.handlers
		#app.logger.setLevel(gunicorn_logger.level)
		my_logger.info("STARTING SERVER")

	if __name__ == '__main__':

		if False:
			import cProfile, pstats
			profiler = cProfile.Profile()
			profiler.enable()

		app.logger.info("Launching server...")
		
		socketio.run(app, host="0.0.0.0", debug=False)
		
		if False:
			profiler.disable()
			stats = pstats.Stats(profiler).sort_stats('ncalls')
			stats.dump_stats('profiling.txt')
			#stats.print_stats()