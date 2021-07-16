import logging
import base64
from flask_socketio import Namespace, emit

class VideoStreamNamespace(Namespace):

	logger = logging.getLogger(__name__)
	logger.info('class VideoStreamNamespace')
	
	connection_count = 0

	def __init__(self, namespace):
		VideoStreamNamespace.logger.info("+ Init VideoStreamNamespace")
		super(Namespace, self).__init__(namespace)
		
		self.frame_count = 0

	def on_connect(self):
		
		VideoStreamNamespace.logger.info("+ /video_stream: connection: Starting video stream " + str(VideoStreamNamespace.connection_count))
		

	def on_disconnect(self):

		VideoStreamNamespace.connection_count -= 1
		VideoStreamNamespace.logger.info("+ /video_stream disconnect " + str(VideoStreamNamespace.connection_count))


	def on_frame(self, frame):
		
		self.frame_count += 1

		VideoStreamNamespace.logger.info("+ /video_stream: Frame received " + str(self.frame_count))

		emit('frame', {'frame' : base64.b64encode(frame).decode("utf-8") }, namespace='/video_cast', broadcast=True)
		
		VideoStreamNamespace.logger.info("+ /video_cast: Frame sent ")


		