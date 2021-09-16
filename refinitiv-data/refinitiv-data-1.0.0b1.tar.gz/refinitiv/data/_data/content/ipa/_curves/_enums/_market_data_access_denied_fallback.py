# coding: utf8

__all__ = ["MarketDataAccessDeniedFallback"]

from enum import Enum, unique
from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class MarketDataAccessDeniedFallback(Enum):
    IGNORE_CONSTITUENTS = "IgnoreConstituents"
    RETURN_ERROR = "ReturnError"
    USE_DELAYED_DATA = "UseDelayedData"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            MarketDataAccessDeniedFallback,
            _MARKET_DATA_ACCESS_DENIED_FALLBACK_VALUES,
            some,
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _MARKET_DATA_ACCESS_DENIED_FALLBACK_VALUES_IN_LOWER_BY_MARKET_DATA_ACCESS_DENIED_FALLBACK,
            some,
        )


_MARKET_DATA_ACCESS_DENIED_FALLBACK_VALUES = tuple(
    t.value for t in MarketDataAccessDeniedFallback
)
_MARKET_DATA_ACCESS_DENIED_FALLBACK_VALUES_IN_LOWER_BY_MARKET_DATA_ACCESS_DENIED_FALLBACK = {
    name.lower(): item
    for name, item in MarketDataAccessDeniedFallback.__members__.items()
}
