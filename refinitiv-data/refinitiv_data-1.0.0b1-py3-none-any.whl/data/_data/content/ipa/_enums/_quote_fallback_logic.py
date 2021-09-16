# coding: utf8
# contract_gen 2020-09-02 06:21:29.297010

__all__ = ["QuoteFallbackLogic"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class QuoteFallbackLogic(Enum):
    """
    Enumeration used to define the fallback logic for the quotation of the instrument.

    Available values are:
    - "None": it means that there's no fallback logic. For example, if the user asks
      for a "Ask" price and instrument is only quoted with a "Bid" price, it is an
      error case.
    - "BestField" : it means that there's a fallback logic to use another market
      data field as quoted price. For example, if the user asks for a "Ask" price
      and instrument is only quoted with a "Bid" price, "Bid" price can be used.
    """

    BEST_FIELD = "BestField"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(QuoteFallbackLogic, _QUOTE_FALLBACK_LOGIC_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _QUOTE_FALLBACK_LOGIC_VALUES_IN_LOWER_BY_QUOTE_FALLBACK_LOGIC, some
        )


_QUOTE_FALLBACK_LOGIC_VALUES = tuple(t.value for t in QuoteFallbackLogic)
_QUOTE_FALLBACK_LOGIC_VALUES_IN_LOWER_BY_QUOTE_FALLBACK_LOGIC = {
    name.lower(): item for name, item in QuoteFallbackLogic.__members__.items()
}
