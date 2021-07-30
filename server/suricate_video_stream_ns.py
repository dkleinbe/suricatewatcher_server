from __future__ import annotations
import logging
import base64
from flask import request
from flask_socketio import Namespace, emit
import typing
if typing.TYPE_CHECKING:
	from suricate_server import Server, SessionId


# FIXME: find a better solution to avoid pylance reporting that sid is not a member of request
def session_id() -> SessionId:
	return request.sid # type: ignore

logger = logging.getLogger('suricate_server.' + __name__)

class SuricateVideoStreamNS(Namespace):

	logger.info('class SuricateVideoStreamNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server : Server):
		logger.info("+ Init SuricateVideoStreamNS")
		super(Namespace, self).__init__(namespace)
		
		self.suricate_server = suricate_server
		self.frame_count = 0

	def on_connect(self):
		
		SuricateVideoStreamNS.connection_count += 1
		self.suricate_server.suricate_count = SuricateVideoStreamNS.connection_count

		logger.info("+ %s: connection [%s]: %d", self.namespace, session_id(), SuricateVideoStreamNS.connection_count)
		
		
	def on_disconnect(self):

		SuricateVideoStreamNS.connection_count -= 1
		self.suricate_server.suricate_count = SuricateVideoStreamNS.connection_count

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateVideoStreamNS.connection_count)

	def on_frame(self, frame):
		""" Reiceve frame from suricate and broadcast to all watcher """
		self.frame_count += 1

		logger.info("+ %s: Frame received: %d", self.namespace, self.frame_count)
		room = self.suricate_server._suricates[frame['id']].room
		#room = frame['id']
		#
		# encode and send frame to all watchers
		#
		emit('frame', {'frame' : base64.b64encode(frame['frame']).decode("utf-8"), 'frame_count': self.frame_count }, 
			namespace='/watcher_video_cast', to=room, include_self=False)
		
		logger.info("+ %s: Frame sent to room: [%s]", self.namespace, room)


		