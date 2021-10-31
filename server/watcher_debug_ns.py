import logging
import base64
from flask_socketio import Namespace, emit
import typing

logger = logging.getLogger(__name__)


class WatcherDebugNS(Namespace):
	
	logger.info('class WatcherDebugNS')

	connection_count = 0

	def __init__(self, namespace, suricate_server):

		logger.info("+ Init WatcherDebugNS")
		super(Namespace, self).__init__(namespace)

		self.suricate_server = suricate_server		

	def on_connect(self):
		
		WatcherDebugNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, WatcherDebugNS.connection_count)

	def on_disconnect(self):

		WatcherDebugNS.connection_count -= 1

		logger.info("+ %s: disconnection: %d", self.namespace, WatcherDebugNS.connection_count)



		