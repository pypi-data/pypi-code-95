# coding: utf8

__all__ = ["EquityDividendType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class EquityDividendType(Enum):
    DEFAULT = "Default"
    DISCRETE = "Discrete"
    YIELD = "Yield"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(EquityDividendType, _EQUITY_DIVIDEND_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _EQUITY_DIVIDEND_TYPE_VALUES_IN_LOWER_BY_EQUITY_DIVIDEND_TYPE, some
        )


_EQUITY_DIVIDEND_TYPE_VALUES = tuple(t.value for t in EquityDividendType)
_EQUITY_DIVIDEND_TYPE_VALUES_IN_LOWER_BY_EQUITY_DIVIDEND_TYPE = {
    name.lower(): item for name, item in EquityDividendType.__members__.items()
}
