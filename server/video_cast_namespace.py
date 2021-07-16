import logging
from flask_socketio import Namespace, emit

class VideoCastNamespace(Namespace):

	logger = logging.getLogger(__name__)
	logger.info('class VideoCastNamespace')
	
	connection_count = 0

	def __init__(self, namespace, sid):
		VideoCastNamespace.logger.info("+ Init VideoCastNamespace")
		super(Namespace, self).__init__(namespace)
		self.suricate_sid = sid

	def on_connect(self):
		
		VideoCastNamespace.logger.info("+ /video_cast: connection: Starting video stream " + str(VideoCastNamespace.connection_count))
		
		emit('start_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=self.suricate_sid)
		VideoCastNamespace.connection_count += 1
		

	def on_disconnect(self):
		VideoCastNamespace.connection_count -= 1
		VideoCastNamespace.logger.info("+ /video_stream disconnect " + str(VideoCastNamespace.connection_count))
		if VideoCastNamespace.connection_count == 0:
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/cmd_suricate', to=self.suricate_sid)

		