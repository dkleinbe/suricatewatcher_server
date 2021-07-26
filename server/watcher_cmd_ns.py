from __future__ import annotations
import logging
from flask import request
from flask_socketio import Namespace, emit, join_room, leave_room, namespace, rooms
from json import JSONEncoder, JSONDecoder
import typing
if typing.TYPE_CHECKING:
	from suricate_server import Server
logger = logging.getLogger('suricate_server.' + __name__)

class WatcherCmdNS(Namespace):
	#
	# namespace 
	#+
	
	logger.info('class WatcherCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server : Server):

		logger.info("+ Init WatcherCmdNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		logger.info("+ %s : connection [%s]: %d", self.namespace, request.sid, WatcherCmdNS.connection_count)
		
		WatcherCmdNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count

		logger.info("+ %s : connection [%s]: %d", self.namespace, request.sid, WatcherCmdNS.connection_count)
		#
		# register watcher
		#
		self.suricate_server.register_watcher(request.sid)

		
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			

	def on_disconnect(self):

		WatcherCmdNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		logger.info("+ %s disconnect: %d", self.namespace, WatcherCmdNS.connection_count)
		print(rooms)
		#
		# stop suricate video stream if this was the last connected watcher
		#
		#if WatcherCmdNS.connection_count == 0:
		#	emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

	def on_suricate_selected(self, suricate):
		
		#aze = JSONDecoder().decode(suricate)
		suricate_id = suricate['suricate_id']
		previous_suricate_id = suricate['previous_suricate_id']
		watcher_sid = suricate['watcher_sid']

		if (previous_suricate_id != 'NONE'):
			self.suricate_server._suricates[previous_suricate_id].remove_watcher(watcher_sid)
						
		if (suricate_id == 'NONE'):
			# Invalide suricate id
			return

		self.suricate_server._suricates[suricate_id].add_watcher(watcher_sid)

		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			
		