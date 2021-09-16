# coding: utf8

__all__ = ["CompoundingType"]

from enum import Enum, unique
from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class CompoundingType(Enum):
    COMPOUNDED = "Compounded"
    CONTINUOUS = "Continuous"
    DISCOUNTED = "Discounted"
    MONEY_MARKET = "MoneyMarket"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CompoundingType, _COMPOUNDING_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_COMPOUNDING_TYPE_VALUES_IN_LOWER_BY_COMPOUNDING_TYPE, some)


_COMPOUNDING_TYPE_VALUES = tuple(t.value for t in CompoundingType)
_COMPOUNDING_TYPE_VALUES_IN_LOWER_BY_COMPOUNDING_TYPE = {
    name.lower(): item for name, item in CompoundingType.__members__.items()
}
