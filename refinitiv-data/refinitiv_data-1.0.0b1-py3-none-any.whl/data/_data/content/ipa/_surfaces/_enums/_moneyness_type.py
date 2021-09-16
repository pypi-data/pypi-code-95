# coding: utf8

__all__ = ["MoneynessType"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class MoneynessType(Enum):
    FWD = "Fwd"
    SIGMA = "Sigma"
    SPOT = "Spot"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(MoneynessType, _MONEYNESS_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_MONEYNESS_TYPE_VALUES_IN_LOWER_BY_MONEYNESS_TYPE, some)


_MONEYNESS_TYPE_VALUES = tuple(t.value for t in MoneynessType)
_MONEYNESS_TYPE_VALUES_IN_LOWER_BY_MONEYNESS_TYPE = {
    name.lower(): item for name, item in MoneynessType.__members__.items()
}
