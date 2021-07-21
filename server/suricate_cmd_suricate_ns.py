import logging
import base64
from flask import request
from flask_socketio import Namespace, emit

logger = logging.getLogger('suricate_server.' + __name__)

class SuricateCmdSuricateNS(Namespace):

	logger.info('class SuricateCmdSuricateNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server):
		logger.info("+ Init SuricateCmdSuricateNS")
		super(Namespace, self).__init__(namespace)
		
		self.suricate_server = suricate_server
		self.suricate_server.suricate_sid = 'NOT_SET'

	def on_connect(self):
		""" 
		We get a suricate 
		"""
		SuricateCmdSuricateNS.connection_count += 1
		
		logger.info("+ %s connect %d with sid: %s", self.namespace, SuricateCmdSuricateNS.connection_count, request.sid)
		
		self.suricate_server.suricate_sid = request.sid
		self.suricate_server.suricate_count = SuricateCmdSuricateNS.connection_count

		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

	def on_disconnect(self):

		SuricateCmdSuricateNS.connection_count -= 1
		self.suricate_server.suricate_count = SuricateCmdSuricateNS.connection_count

		logger.info("+ %s disconnect %d", self.namespace, SuricateCmdSuricateNS.connection_count)

		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)




		