from __future__ import annotations
import logging
from flask import request
from flask_socketio import Namespace, emit, join_room, leave_room, namespace, rooms
from json import JSONEncoder, JSONDecoder
import typing
if typing.TYPE_CHECKING:
	from suricate_server import Server, SessionId


# FIXME: find a better solution to avoid pylance reporting that sid is not a member of request
def session_id() -> SessionId:
	return request.sid # type: ignore

logger = logging.getLogger('suricate_server.' + __name__)

class WatcherCmdNS(Namespace):
	#
	# namespace 
	#+
	
	logger.info('class WatcherCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_server : Server):

		logger.info("+ Init WatcherCmdNS")

		self.suricate_server = suricate_server
		
		super(Namespace, self).__init__(namespace)
		

	def on_connect(self):
		
		logger.info("+ %s : connection [%s]: %d", self.namespace, session_id(), WatcherCmdNS.connection_count)
		
		WatcherCmdNS.connection_count += 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count

		logger.info("+ %s : connection [%s]: %d", self.namespace, session_id(), WatcherCmdNS.connection_count)
		#
		# register watcher
		#
		self.suricate_server.register_watcher(session_id())

		
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=session_id())
			

	def on_disconnect(self):

		WatcherCmdNS.connection_count -= 1
		self.suricate_server.watchers_count = WatcherCmdNS.connection_count
		#
		# Un register watcher, this will also stop watching
		#
		self.suricate_server.unregister_watcher(session_id())

		logger.info("+ %s disconnect: %d", self.namespace, WatcherCmdNS.connection_count)
		
		# update debug data
		emit('update', self.suricate_server.toJSON() , namespace='/debug', broadcast=True, skip_sid=session_id())

	def on_suricate_selected(self, suricate):
		
		suricate_id = suricate['suricate_id']
		previous_suricate_id = suricate['previous_suricate_id']
		watcher_video_cast_sid = suricate['watcher_sid']
		
		self.suricate_server._watchers[session_id()].watch_suricate(watcher_video_cast_sid, 
																	suricate_id)

		# update debug data
		emit('update', self.suricate_server.toJSON(), namespace='/debug', broadcast=True, skip_sid=session_id())

	def on_joystick_state(self, data):
		"""
		called when joystick starts and ends
		"""
		state_data = data['data']
		id = data['joystick_id']
		evt = data['evt']
		logger.info("+ joystick[%s] evt type: [%s] position: %s", id, evt['type'], state_data['position'])

		if evt['type'] == 'start':
			self.suricate_server._watchers[session_id()].start_cam_ctrl(state_data)
		else:
			self.suricate_server._watchers[session_id()].stop_cam_ctrl(state_data)

	def on_joystick_move(self, data):
		""" 
		called when joystick moves
		"""
		move_data = data['data']
		id = data['joystick_id']
		logger.info("+ joystick[%s] moved force: %.2f position %s", id, move_data['force'], move_data['position'])

		self.suricate_server._watchers[session_id()].move_cam(data)
			
		