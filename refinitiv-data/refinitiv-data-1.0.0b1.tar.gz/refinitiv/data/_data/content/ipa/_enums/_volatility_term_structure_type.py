# coding: utf8

__all__ = ["VolatilityTermStructureType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class VolatilityTermStructureType(Enum):
    HISTORICAL = "Historical"
    IMPLIED = "Implied"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            VolatilityTermStructureType, _VOLATILITY_TERM_STRUCTURE_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _VOLATILITY_TERM_STRUCTURE_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_TERM_STRUCTURE_TYPE,
            some,
        )


_VOLATILITY_TERM_STRUCTURE_TYPE_VALUES = tuple(
    t.value for t in VolatilityTermStructureType
)
_VOLATILITY_TERM_STRUCTURE_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_TERM_STRUCTURE_TYPE = {
    name.lower(): item for name, item in VolatilityTermStructureType.__members__.items()
}
