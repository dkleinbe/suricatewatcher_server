import logging
from flask import request
from flask_socketio import Namespace, emit
from json import JSONEncoder


class WatcherVideoCastNS(Namespace):
	#
	# namespace to cast images to suricate watchers clients
	#
	logger = logging.getLogger('suricate_server.' + __name__)
	logger.info('class WatcherVideoCastNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server):

		WatcherVideoCastNS.logger.info("+ Init WatcherVideoCastNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		WatcherVideoCastNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		WatcherVideoCastNS.logger.info("+ /video_cast: connection: " + str(WatcherVideoCastNS.connection_count))
		WatcherVideoCastNS.logger.info("+ /video_cast: starting suricate stream: " + str(suricate_sid))
		WatcherVideoCastNS.logger.info("+ /video_cast: " + self.suricate_server.toJSON())
		#
		# start suricate video stream
		#
		emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)
		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=request.sid)
			

	def on_disconnect(self):

		WatcherVideoCastNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherVideoCastNS.connection_count

		suricate_sid = self.suricate_server.suricate_sid

		WatcherVideoCastNS.logger.info("+ /video_cast disconnect: " + str(WatcherVideoCastNS.connection_count))
		#
		# stop suricate video stream if this was the last connected watcher
		#
		if WatcherVideoCastNS.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

		