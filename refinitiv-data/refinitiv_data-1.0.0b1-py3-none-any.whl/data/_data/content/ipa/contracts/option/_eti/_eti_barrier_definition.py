# coding: utf8

__all__ = ["EtiBarrierDefinition"]

from typing import Optional

from .._base import BarrierDefinition
from .._enums import (
    BarrierStyle,
    InOrOut,
    UpOrDown,
)


class EtiBarrierDefinition(BarrierDefinition):
    """
    Parameters
    ----------
    barrier_style : BarrierStyle, optional

    in_or_out : InOrOut, optional

    up_or_down : UpOrDown, optional

    level : float, optional

    """

    def __init__(
        self,
        barrier_style: Optional[BarrierStyle] = None,
        in_or_out: Optional[InOrOut] = None,
        up_or_down: Optional[UpOrDown] = None,
        level: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.barrier_style = barrier_style
        self.in_or_out = in_or_out
        self.up_or_down = up_or_down
        self.level = level

    @property
    def barrier_style(self):
        """
        :return: enum BarrierStyle
        """
        return self._get_enum_parameter(BarrierStyle, "barrierStyle")

    @barrier_style.setter
    def barrier_style(self, value):
        self._set_enum_parameter(BarrierStyle, "barrierStyle", value)

    @property
    def in_or_out(self):
        """
        :return: enum InOrOut
        """
        return self._get_enum_parameter(InOrOut, "inOrOut")

    @in_or_out.setter
    def in_or_out(self, value):
        self._set_enum_parameter(InOrOut, "inOrOut", value)

    @property
    def up_or_down(self):
        """
        :return: enum UpOrDown
        """
        return self._get_enum_parameter(UpOrDown, "upOrDown")

    @up_or_down.setter
    def up_or_down(self, value):
        self._set_enum_parameter(UpOrDown, "upOrDown", value)

    @property
    def level(self):
        """
        :return: float
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)
