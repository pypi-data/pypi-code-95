# coding: utf8

__all__ = ["FxDoubleBarrierDefinition"]

from typing import Optional

from ...instrument._instrument_definition import ObjectDefinition
from .._enums import BarrierMode
from ._fx_double_barrier_info import FxDoubleBarrierInfo


class FxDoubleBarrierDefinition(ObjectDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    barrier_down : FxDoubleBarrierInfo, optional
        Barrier Information for the lower barrier
    barrier_mode : BarrierMode, optional
        Barrier Mode of the double barrier option
    barrier_up : FxDoubleBarrierInfo, optional
        Barrier Information for the upper barrier
    """

    def __init__(
        self,
        barrier_down: Optional[FxDoubleBarrierInfo] = None,
        barrier_mode: Optional[BarrierMode] = None,
        barrier_up: Optional[FxDoubleBarrierInfo] = None,
    ) -> None:
        super().__init__()
        self.barrier_down = barrier_down
        self.barrier_mode = barrier_mode
        self.barrier_up = barrier_up

    @property
    def barrier_down(self):
        """
        Barrier Information for the lower barrier
        :return: object FxDoubleBarrierInfo
        """
        return self._get_object_parameter(FxDoubleBarrierInfo, "barrierDown")

    @barrier_down.setter
    def barrier_down(self, value):
        self._set_object_parameter(FxDoubleBarrierInfo, "barrierDown", value)

    @property
    def barrier_mode(self):
        """
        Barrier Mode of the double barrier option
        :return: enum BarrierMode
        """
        return self._get_enum_parameter(BarrierMode, "barrierMode")

    @barrier_mode.setter
    def barrier_mode(self, value):
        self._set_enum_parameter(BarrierMode, "barrierMode", value)

    @property
    def barrier_up(self):
        """
        Barrier Information for the upper barrier
        :return: object FxDoubleBarrierInfo
        """
        return self._get_object_parameter(FxDoubleBarrierInfo, "barrierUp")

    @barrier_up.setter
    def barrier_up(self, value):
        self._set_object_parameter(FxDoubleBarrierInfo, "barrierUp", value)
