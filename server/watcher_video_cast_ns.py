import logging
from flask import request
from flask_socketio import Namespace, emit
from json import JSONEncoder

logger = logging.getLogger('suricate_server.' + __name__)

class WatcherVideoCastNS(Namespace):
	#
	# namespace to cast images to suricate watchers clients
	#
	
	logger.info('class WatcherVideoCastNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server):

		logger.info("+ Init WatcherVideoCastNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		WatcherVideoCastNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		logger.info("+ %s : connection: %d", self.namespace, WatcherVideoCastNS.connection_count)
		#
		# start suricate video stream
		#
		logger.info("+ %s: starting suricate stream: %s", self.namespace, suricate_sid)

		emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=suricate_sid)

		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			

	def on_disconnect(self):

		WatcherVideoCastNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		logger.info("+ %s disconnect: %d", self.namespace, WatcherVideoCastNS.connection_count)
		#
		# stop suricate video stream if this was the last connected watcher
		#
		if WatcherVideoCastNS.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

		