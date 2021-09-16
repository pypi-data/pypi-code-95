# coding: utf8

__all__ = ["DividendType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class DividendType(Enum):
    FORECAST_TABLE = "ForecastTable"
    FORECAST_YIELD = "ForecastYield"
    FUTURES = "Futures"
    HISTORICAL_YIELD = "HistoricalYield"
    IMPLIED_TABLE = "ImpliedTable"
    IMPLIED_YIELD = "ImpliedYield"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DividendType, _DIVIDEND_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DIVIDEND_TYPE_VALUES_IN_LOWER_BY_DIVIDEND_TYPE, some)


_DIVIDEND_TYPE_VALUES = tuple(t.value for t in DividendType)
_DIVIDEND_TYPE_VALUES_IN_LOWER_BY_DIVIDEND_TYPE = {
    name.lower(): item for name, item in DividendType.__members__.items()
}
