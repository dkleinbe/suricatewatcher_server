from __future__ import annotations
import logging
import base64
from flask import request
from flask_socketio import Namespace, emit, namespace
import typing
if typing.TYPE_CHECKING:
	from suricate_server import Server

logger = logging.getLogger('suricate_server.' + __name__)

class SuricateCmdNS(Namespace):

	logger.info('class SuricateCmdSuricateNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server : Server):
		logger.info("+ Init SuricateCmdSuricateNS")
		super(Namespace, self).__init__(namespace)
		
		self.suricate_server = suricate_server
		self.suricate_server.suricate_sid = 'NOT_SET'

	def on_connect(self, auth):
		 
		#We get a suricate cd 
		
		SuricateCmdNS.connection_count += 1
		self.suricate_server.suricate_count = SuricateCmdNS.connection_count

		logger.info("+ %s connect %d with sid: %s", self.namespace, SuricateCmdNS.connection_count, request.sid)
		#id = auth['id']
		id = request.sid
		logger.info("+ Suricate id: " + str(id))

		#
		# Add suricate to server with cmd_session id
		#
		self.suricate_server.register_suricate(request.sid)
		
		emit('suricate_id', { 'suricate_id' : id })
		#
		# tell to all watchers we have a new suricate to watch
		#
		emit('add_suricate', 
			{'suricate_id' : id, 'name' : 'suricate_' + str(self.suricate_server.suricate_count)}, 
			namespace='/watcher_cmd', 
			broadcast=True, 
			skip_sid=request.sid)
				
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)

	def on_disconnect(self):

		logger.info("+ %s disconnect %d", self.namespace, SuricateCmdNS.connection_count)

		SuricateCmdNS.connection_count -= 1
		self.suricate_server.suricate_count = SuricateCmdNS.connection_count
		id = self.suricate_server.suricate_id(request.sid).suricate_cmd_sid
		#
		# tell to all watchers  suricate has gone
		#		
		emit('remove_suricate',
			{'suricate_id' : id },
			namespace='/watcher_cmd',
			broadcast=True, 
			skip_sid=request.sid)
		
		self.suricate_server.unregister_suricate(id)

		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=request.sid)




		