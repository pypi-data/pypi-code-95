import numpy as np

from . import config as c
from .gui_attributes import Gui_attributes


class Obstacle(object):
    def __init__(
        self,
        id,
        position,
        radius=0.06,
        color=None,
    ):
        self.id = id
        self.gui_att = Gui_attributes(
            mode=0,
            num_thrusts=0,
            thrust_directions=None,
            radius=radius,
            color=color)
        self.position = position
        self.radius = radius
        self.gui_att.update_position(self.position, None, np.zeros(
                                         [c.INPUT_MOTOR_DIM]))
