from my_types import SessionId
from suricate import Suricate
from transitions import Machine, State
from typing import Optional




class CamController(object):

    # The states
    states=[
        State(name='init', ignore_invalid_triggers=True),
        State(name='cam_ctrl', on_enter='send_move_cam')
        ]
    # And some transitions between states. We're lazy, so we'll leave out
    # the inverse phase transitions (freezing, condensation, etc.).
    transitions = [
        { 'trigger': 'start_cam_ctrl', 'source': 'init', 'dest': 'cam_ctrl', 'conditions': 'is_cam_free', 'after': 'send_start_cam_ctr'},
        { 'trigger': 'stop_cam_ctrl', 'source': 'cam_ctrl', 'dest': 'init', 'after': 'send_stop_cam_ctr'},
        { 'trigger': 'move_cam', 'source': 'cam_ctrl', 'dest': 'cam_ctrl' },
    ]

    def __init__(self) -> None:
        super().__init__()

        self.suricate : Optional[Suricate] = None

        self.sm = Machine(
            model=self, 
            states=CamController.states, 
            transitions=CamController.transitions, 
            initial='init')
    
    def is_cam_free(self, suricate : Suricate) -> bool:
        self.suricate = suricate
        return not suricate.is_cam_in_use

    def send_start_cam_ctr(self, data):
        if self.suricate is not None:
            self.suricate.start_cam_ctrl(data)

    def send_stop_cam_ctr(self, data):
        if self.suricate is not None:
            self.suricate.stop_cam_ctrl(data)

    def send_move_cam(self, data):
        if self.suricate is not None:
            self.suricate.move_cam(data)
