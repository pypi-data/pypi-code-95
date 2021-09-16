# coding: utf8

__all__ = ["CreditSpreadType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class CreditSpreadType(Enum):
    FLAT_SPREAD = "FlatSpread"
    TERM_STRUCTURE = "TermStructure"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CreditSpreadType, _CREDIT_SPREAD_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _CREDIT_SPREAD_TYPE_VALUES_IN_LOWER_BY_CREDIT_SPREAD_TYPE, some
        )


_CREDIT_SPREAD_TYPE_VALUES = tuple(t.value for t in CreditSpreadType)
_CREDIT_SPREAD_TYPE_VALUES_IN_LOWER_BY_CREDIT_SPREAD_TYPE = {
    name.lower(): item for name, item in CreditSpreadType.__members__.items()
}
