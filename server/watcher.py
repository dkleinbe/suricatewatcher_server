from __future__ import annotations
import logging
import typing

from typing import Optional

from  my_types import SessionId
from suricate import Suricate
if typing.TYPE_CHECKING:
	from suricate_server import Server

logger = logging.getLogger('suricate_server.' + __name__)

class Watcher:
	def __init__(self, id : SessionId, suricate_server : Server):

		self.id : SessionId = id
		self.suricate_server = suricate_server
		self.watcher_cmd_sid        : SessionId = SessionId('NONE')
		self.watcher_video_cast_sid : SessionId = SessionId('NONE')
		self.watched_suricate_id    : SessionId = SessionId('NONE')
		self.watched_suricate       : Optional[Suricate] = None
		
	def watch_suricate(self, watcher_video_cast_sid : SessionId, suricate_sid : SessionId) -> None:

		# if we are already watching a suricate, stop watching
		if (self.watched_suricate != None) :
			
			self.stop_watching()

		# Stop watching
		if (suricate_sid == 'NONE'):
			return

		self.watcher_video_cast_sid = watcher_video_cast_sid
		# TODO: check if we have a valid suricate_sid: do self.suricate_server._suricates[suricate_sid] exist?
		suricate = self.suricate_server._suricates[suricate_sid]
		suricate.add_watcher(self.watcher_video_cast_sid)
		self.watched_suricate = suricate
	
	def stop_watching(self) -> None :

		if (self.watched_suricate != None):
			self.watched_suricate.remove_watcher(self.watcher_video_cast_sid)
		self.watched_suricate = None

	def start_cam_ctrl(self, data):
		
		if (self.watched_suricate != None):
			logger.info("+ Watcher [%s] start cmd ctrl", self.id)
			self.watched_suricate.start_cam_ctrl()
		else:
			logger.error('- No watcher suricate')	

	def stop_cam_ctrl(self, data):

		if (self.watched_suricate != None):
			logger.debug("+ Watcher [%s] end cmd ctrl", self.id)
			self.watched_suricate.stop_cam_ctrl()
		else:
			logger.error('- No watcher suricate')	

	def move_cam(self, data):
		vector = data['data']['vector']
				
		if (self.watched_suricate != None):
			logger.info("+ Watcher [%s] move cam x: %.4f y: %.4f", self.id, vector['x'], vector['y'])
			self.watched_suricate.move_cam(vector)
		else:
			logger.error('- No watcher suricate')

