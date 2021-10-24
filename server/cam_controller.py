from transitions import Machine, State

from .my_types import SessionId

import typing
if typing.TYPE_CHECKING:
    from .suricate import Suricate


class CamController(object):

    # The states
    states=[
        State(name='init', ignore_invalid_triggers=True), # , ignore_invalid_triggers=True
        State(name='cam_ctrl', ignore_invalid_triggers=True)
        ]
    # And some transitions between states. We're lazy, so we'll leave out
    # the inverse phase transitions (freezing, condensation, etc.).
    transitions = [
        { 'trigger': 'evt_start_cam_ctrl', 'source': 'init', 'dest': 'cam_ctrl', 'conditions': 'is_cam_free', 'after': 'start_cam_ctr'},
        { 'trigger': 'evt_stop_cam_ctrl', 'source': 'cam_ctrl', 'dest': 'init', 'after': 'stop_cam_ctr'},
        { 'trigger': 'evt_move_cam', 'source': 'cam_ctrl', 'dest': 'cam_ctrl', 'after': 'move_cam' },
    ]

    _is_cam_free : bool = True

    def __init__(self, suricate) -> None:
        super().__init__()

        self.suricate     : Suricate = suricate
        CamController._is_cam_free  : bool = True
        self.sm = Machine(
            model=self, 
            states=CamController.states, 
            transitions=CamController.transitions, 
            initial='init')
    
    def is_cam_free(self) -> bool:
        
        return  CamController._is_cam_free

    def start_cam_ctr(self):
        if self.suricate is not None:
            CamController._is_cam_free = False
            self.suricate.do_start_cam_ctrl()

    def stop_cam_ctr(self):
        if self.suricate is not None:
            CamController._is_cam_free = True
            self.suricate.do_stop_cam_ctrl()

    def move_cam(self, data):
        if self.suricate is not None:
            self.suricate.do_move_cam(data)
