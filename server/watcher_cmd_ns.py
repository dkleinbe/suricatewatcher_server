import logging
from flask import request
from flask_socketio import Namespace, emit, join_room, leave_room, namespace
from json import JSONEncoder, JSONDecoder

logger = logging.getLogger('suricate_server.' + __name__)

class WatcherCmdNS(Namespace):
	#
	# namespace 
	#+
	
	logger.info('class WatcherCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server):

		logger.info("+ Init WatcherCmdNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		WatcherCmdNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count
	
		logger.info("+ %s : connection [%s]: %d", self.namespace, request.sid, WatcherCmdNS.connection_count)
		
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			

	def on_disconnect(self):

		WatcherCmdNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		logger.info("+ %s disconnect: %d", self.namespace, WatcherCmdNS.connection_count)
		#
		# stop suricate video stream if this was the last connected watcher
		#
		if WatcherCmdNS.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

	def on_suricate_selected(self, suricate):
		
		#aze = JSONDecoder().decode(suricate)
		suricate_id = suricate['suricate_id']
		previous_suricate_id = suricate['previous_suricate_id']
		watcher_sid = suricate['watcher_sid']

		if (previous_suricate_id != 'NONE'):
			# watcher was watching an other suricate, lets leave the room
			logger.debug('+ removing watcher from room <%s>', previous_suricate_id)
			leave_room(sid=watcher_sid, room=previous_suricate_id, namespace='/watcher_video_cast')
		
		if (suricate_id == 'NONE'):
			# Invalide suricate id
			return

		session_id = self.suricate_server._suricates[suricate_id].sid_cmd
					
		#
		# add watcher to suricat room
		#
		logger.info('+ Entering room [%s]', suricate_id)
		join_room(sid=watcher_sid, room=suricate_id, namespace='/watcher_video_cast')		
		#
		# start suricate video stream
		#
		logger.info("+ %s: starting suricate stream: %s", self.namespace, session_id)
		emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=session_id)


		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			
		