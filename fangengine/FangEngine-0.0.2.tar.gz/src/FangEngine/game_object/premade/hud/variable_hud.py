import typing

import pygame
import collections
import abc

import FangEngine.game_object.premade.hud.hud_base as hud_base


class VariableHUD(hud_base.HUDBase):
    def __init__(self, screen_parent, x: float, y: float, w: float, h: float):
        raise NotImplementedError("Coming Soon")

        super().__init__(screen_parent, x, y, w, h)
        self.metrics = collections.OrderedDict()        # type: typing.Dict[str, callable]

    def add_metric(self, name: str, function: callable) -> 'VariableHUD':
        self.metrics[name] = function
        return self
