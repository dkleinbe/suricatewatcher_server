from __future__ import annotations
import logging
import typing
from typing import List
from flask_socketio import join_room, leave_room, emit

from .filters import ButterFilter
from .cam_controller import CamController
from .my_types import SessionId

if typing.TYPE_CHECKING:
	from .watcher import Watcher

logger = logging.getLogger(__name__)

class Suricate:

	def __init__(self, sid : SessionId) -> None:
		""" init a Suricat.

		:param sid: The session id of the suricate_cmd namespace.

		"""
		self.id                        : SessionId = sid
		self.room                      : str = 'room_' + sid # create room name from sid
		self.suricate_cmd_sid          : SessionId = sid
		self.suricate_video_stream_sid : SessionId = SessionId('NONE')
		self.watchers                  : List[Watcher] = []
		self.distance_filter           : ButterFilter = ButterFilter()
		
	def add_watcher(self, watcher : Watcher) -> None:
		""" Adds a watcher to the suricate

		The watcher is added to the suricate video cast room

		Args
			watcher (`Watcher`): the watcher
		"""
		
		#
		# add watcher to suricat room
		#
		logger.info('+ Entering room [%s]', self.room)
		join_room(sid=watcher.watcher_video_cast_sid, room=self.room, namespace='/watcher_video_cast')
		join_room(sid=watcher.id, room=self.room, namespace='/watcher_cmd')

		# add watcher to watcher list
		self.watchers.append(watcher)

		#
		# start suricate video stream
		#
		if len(self.watchers) == 1 : 
			logger.info("+ starting suricate stream: %s", self.suricate_cmd_sid)
			emit('start_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def remove_watcher(self, watcher : Watcher):

		# lets leave the room
		logger.info('+ removing watcher from room <%s>', self.room)
		leave_room(sid=watcher.watcher_video_cast_sid, room=self.room, namespace='/watcher_video_cast')
		leave_room(sid=watcher.id, room=self.room, namespace='/watcher_cmd')

		# remove watcher from watcher list
		self.watchers.remove(watcher)
		
		if (len(self.watchers) <= 0):
			# if no more watcher for this suricate stop video stream
			emit('stop_video_stream', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def do_start_cam_ctrl(self):

		logger.debug("+ Suricate [%s] start cmd ctrl", self.id)
		self.is_cam_in_use = True
		emit('start_cam_ctrl', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)
	
	def do_stop_cam_ctrl(self):

		logger.debug("+ Suricate [%s] start cmd ctrl", self.id)
		self.is_cam_in_use = False
		emit('stop_cam_ctrl', {'payload' : 'aze'}, namespace='/suricate_cmd', to=self.suricate_cmd_sid)
	
	def do_move_cam(self, data):

		logger.debug("+ Suricate [%s] start move cam", self.id)
		
		emit('move_cam', data, namespace='/suricate_cmd', to=self.suricate_cmd_sid)

	def emit_data(self, data):

		#data['distance_filtered'] = self.filter_distance(data['distance_sensor'])

		room = self.room

		emit('suricate_data', data, 
		     namespace='/watcher_cmd', to=room, include_self=False)

		pass

	def filter_distance(self, distance):

		return self.distance_filter.push_data(distance)