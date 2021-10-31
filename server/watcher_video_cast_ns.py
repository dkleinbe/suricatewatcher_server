from __future__ import annotations
import logging
from flask import request
from flask_socketio import Namespace, emit, rooms
from json import JSONEncoder
import typing
if typing.TYPE_CHECKING:
	from suricate_server import Server, SessionId


# FIXME: find a better solution to avoid pylance reporting that sid is not a member of request
def session_id() -> SessionId:
	return request.sid # type: ignore

logger = logging.getLogger(__name__)

class WatcherVideoCastNS(Namespace):
	#
	# namespace to cast images to suricate watchers clients
	#
	
	logger.info('class WatcherVideoCastNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server : Server):

		logger.info("+ Init WatcherVideoCastNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		WatcherVideoCastNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		logger.info("+ %s : connection: %d", self.namespace, WatcherVideoCastNS.connection_count)
		#
		# start suricate video stream
		#
		##### logger.info("+ %s: starting suricate stream: %s", self.namespace, suricate_sid)

		##### emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=suricate_sid)

		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=session_id())
			

	def on_disconnect(self):

		WatcherVideoCastNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		logger.info("+ %s disconnect: %d", self.namespace, WatcherVideoCastNS.connection_count)
		#
		# stop suricate video stream if this was the last connected watcher
		#
		#if WatcherVideoCastNS.connection_count == 0:
		#	emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)

		logger.debug('+ rooms: %s', rooms())
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=session_id())

		