import logging
from flask_socketio import Namespace, emit

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

		suricate_sid = self.suricate_server.get_suricate_sid()

		WatcherVideoCastNS.logger.info("+ /video_cast: connection: " + str(WatcherVideoCastNS.connection_count))
		WatcherVideoCastNS.logger.info("+ /video_cast: starting suricate stream: " + str(suricate_sid))

		emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=suricate_sid)

		emit('update', namespace='/debug', broadcast=True)
			

	def on_disconnect(self):

		WatcherVideoCastNS.connection_count -= 1

		WatcherVideoCastNS.logger.info("+ /video_cast disconnect: " + str(WatcherVideoCastNS.connection_count))

		if WatcherVideoCastNS.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=self.suricate_sid)

		