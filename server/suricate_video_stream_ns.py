import logging
import base64
from flask_socketio import Namespace, emit

class SuricateVideoStreamNS(Namespace):

	logger = logging.getLogger('suricate_server.' + __name__)
	logger.info('class SuricateVideoStreamNS')
	
	connection_count = 0

	def __init__(self, namespace):
		SuricateVideoStreamNS.logger.info("+ Init SuricateVideoStreamNS")
		super(Namespace, self).__init__(namespace)
		
		self.frame_count = 0

	def on_connect(self):
		
		SuricateVideoStreamNS.connection_count += 1

		SuricateVideoStreamNS.logger.info("+ /video_stream: connection: Starting video stream: " + str(SuricateVideoStreamNS.connection_count))

	def on_disconnect(self):

		SuricateVideoStreamNS.connection_count -= 1

		SuricateVideoStreamNS.logger.info("+ /video_stream disconnect " + str(SuricateVideoStreamNS.connection_count))


	def on_frame(self, frame):
		""" Reiceve frame from suricate and broadcast to all watcher """
		self.frame_count += 1

		SuricateVideoStreamNS.logger.info("+ /video_stream: Frame received " + str(self.frame_count))
		#
		# encode and send frame to all watchers
		#
		emit('frame', {'frame' : base64.b64encode(frame).decode("utf-8") }, namespace='/video_cast', broadcast=True)
		
		SuricateVideoStreamNS.logger.info("+ /video_cast: Frame sent ")


		