# coding: utf8

__all__ = ["OptionVolatilityType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class OptionVolatilityType(Enum):
    HISTORICAL = "Historical"
    IMPLIED = "Implied"
    SVI_SURFACE = "SVISurface"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            OptionVolatilityType, _OPTION_VOLATILITY_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _OPTION_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_OPTION_VOLATILITY_TYPE, some
        )


_OPTION_VOLATILITY_TYPE_VALUES = tuple(t.value for t in OptionVolatilityType)
_OPTION_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_OPTION_VOLATILITY_TYPE = {
    name.lower(): item for name, item in OptionVolatilityType.__members__.items()
}
