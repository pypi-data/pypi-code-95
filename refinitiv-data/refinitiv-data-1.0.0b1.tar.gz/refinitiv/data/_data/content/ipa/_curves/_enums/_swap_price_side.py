# coding: utf8

__all__ = ["SwapPriceSide"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class SwapPriceSide(Enum):
    ASK = "Ask"
    BID = "Bid"
    MID = "Mid"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(SwapPriceSide, _SWAP_PRICE_SIDE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_SWAP_PRICE_SIDE_VALUES_IN_LOWER_BY_SWAP_PRICE_SIDE, some)


_SWAP_PRICE_SIDE_VALUES = tuple(t.value for t in SwapPriceSide)
_SWAP_PRICE_SIDE_VALUES_IN_LOWER_BY_SWAP_PRICE_SIDE = {
    name.lower(): item for name, item in SwapPriceSide.__members__.items()
}
