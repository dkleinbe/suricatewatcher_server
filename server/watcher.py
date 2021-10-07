from __future__ import annotations
import logging
from cam_controller import CamController
import typing

from typing import Optional

from my_types import SessionId
from suricate import Suricate

if typing.TYPE_CHECKING:
	from suricate_server import Server
	

logger = logging.getLogger('suricate_server.' + __name__)

class Watcher:
	def __init__(self, watcher_cmd_sid : SessionId, suricate_server : Server):
		""" init a Suricat.

			:param watcher_cmd_sid: The session id of the watcher_cmd namespace.

		"""
		self.id                     : SessionId  = watcher_cmd_sid
		self.watcher_video_cast_sid : SessionId = SessionId('NONE')
		
		self.suricate_server = suricate_server
		
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
		suricate.add_watcher(self)
		self.watched_suricate = suricate
		self.cam_controler : CamController = CamController(suricate)

	def stop_watching(self) -> None :

		if (self.watched_suricate != None):
			self.watched_suricate.remove_watcher(self)
		self.watched_suricate = None

	def start_cam_ctrl(self, data):
		
		if (self.watched_suricate != None):

			logger.info("+ Watcher [%s] start cmd ctrl", self.id)
			
			self.cam_controler.evt_start_cam_ctrl()
		else:
			logger.error('- No watcher suricate')	

	def stop_cam_ctrl(self, data):

		if (self.watched_suricate != None):

			logger.info("+ Watcher [%s] end cmd ctrl", self.id)

			self.cam_controler.evt_stop_cam_ctrl()
		else:
			logger.error('- No watcher suricate')	

	def move_cam(self, data):
		vector = data['data']['vector']
				
		if (self.watched_suricate != None):
			logger.debug("+ Watcher [%s] move cam x: %.4f y: %.4f", self.id, vector['x'], vector['y'])
			self.cam_controler.evt_move_cam(vector)
		else:
			logger.error('- No watcher suricate')

