import logging
import base64
from flask_socketio import Namespace, emit

logger = logging.getLogger('suricate_server.' + __name__)

class SuricateVideoStreamNS(Namespace):

	logger.info('class SuricateVideoStreamNS')
	
	connection_count = 0

	def __init__(self, namespace):
		logger.info("+ Init SuricateVideoStreamNS")
		super(Namespace, self).__init__(namespace)
		
		self.frame_count = 0

	def on_connect(self):
		
		SuricateVideoStreamNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateVideoStreamNS.connection_count)

	def on_disconnect(self):

		SuricateVideoStreamNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateVideoStreamNS.connection_count)

	def on_frame(self, frame):
		""" Reiceve frame from suricate and broadcast to all watcher """
		self.frame_count += 1

		logger.info("+ %s: Frame received: %d", self.namespace, self.frame_count)
		#
		# encode and send frame to all watchers
		#
		emit('frame', {'frame' : base64.b64encode(frame).decode("utf-8") }, namespace='/video_cast', broadcast=True)
		
		logger.info("+ %s: Frame sent ", self.namespace)


		