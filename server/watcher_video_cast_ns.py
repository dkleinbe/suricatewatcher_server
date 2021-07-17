import logging
from flask_socketio import Namespace, emit

class WatcherVideoCastNS(Namespace):
	#
	# namespace to cast images to suricate watchers clients
	#
	logger = logging.getLogger(__name__)
	logger.info('class WatcherVideoCastNS')
	
	connection_count = 0

	def __init__(self, namespace, sid):

		WatcherVideoCastNS.logger.info("+ Init WatcherVideoCastNS")

		self.suricate_sid = sid

		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		WatcherVideoCastNS.connection_count += 1

		WatcherVideoCastNS.logger.info("+ /video_cast: connection: " + str(WatcherVideoCastNS.connection_count))

		emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=self.suricate_sid)

		emit('update', namespace='/debug', broadcast=True)
			

	def on_disconnect(self):

		WatcherVideoCastNS.connection_count -= 1

		WatcherVideoCastNS.logger.info("+ /video_cast disconnect: " + str(WatcherVideoCastNS.connection_count))

		if WatcherVideoCastNS.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=self.suricate_sid)

		