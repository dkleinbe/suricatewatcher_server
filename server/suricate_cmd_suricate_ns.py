import logging
import base64
from flask import request
from flask_socketio import Namespace, emit


class SuricateCmdSuricateNS(Namespace):

	logger = logging.getLogger('suricate_server.' + __name__)
	logger.info('class SuricateCmdSuricateNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server):
		SuricateCmdSuricateNS.logger.info("+ Init SuricateCmdSuricateNS")
		super(Namespace, self).__init__(namespace)
		
		self.suricate_server = suricate_server
		self.suricate_server.set_suricate_sid(123)

	def on_connect(self):
		""" 
		We get a suricate 
		"""
		SuricateCmdSuricateNS.connection_count += 1
		
		SuricateCmdSuricateNS.logger.info("+ /cmd_suricate: connect with sid: " + str(request.sid))
		
		self.suricate_server.set_suricate_sid(request.sid)

		emit('update', namespace='/debug', broadcast=True)

	def on_disconnect(self):

		SuricateCmdSuricateNS.connection_count -= 1

		SuricateCmdSuricateNS.logger.info("+ /cmd_suricate disconnect " + str(SuricateCmdSuricateNS.connection_count))




		