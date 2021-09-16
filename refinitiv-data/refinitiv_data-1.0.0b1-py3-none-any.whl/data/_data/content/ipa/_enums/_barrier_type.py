# coding: utf8

__all__ = ["BarrierType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class BarrierType(Enum):
    KNOCK_IN = "KnockIn"
    KNOCK_IN_KNOCK_OUT = "KnockInKnockOut"
    KNOCK_OUT = "KnockOut"
    KNOCK_OUT_KNOCK_IN = "KnockOutKnockIn"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BarrierType, _BARRIER_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_BARRIER_TYPE_VALUES_IN_LOWER_BY_BARRIER_TYPE, some)


_BARRIER_TYPE_VALUES = tuple(t.value for t in BarrierType)
_BARRIER_TYPE_VALUES_IN_LOWER_BY_BARRIER_TYPE = {
    name.lower(): item for name, item in BarrierType.__members__.items()
}
