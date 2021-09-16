# coding: utf8

__all__ = ["SurfaceOutputs"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class SurfaceOutputs(Enum):
    HEADERS = "Headers"
    DATATYPE = "DataType"
    DATA = "Data"
    STATUSES = "Statuses"
    FORWARD_CURVE = "ForwardCurve"
    DIVIDENDS = "Dividends"
    INTEREST_RATE_CURVE = "InterestRateCurve"
    GOODNESS_OF_FIT = "GoodnessOfFit"
    UNDERLYING_SPOT = "UnderlyingSpot"
    DISCOUNT_CURVE = "DiscountCurve"
    MONEYNESS_STRIKE = "MoneynessStrike"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(SurfaceOutputs, _SURFACE_OUTPUTS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_SURFACE_OUTPUTS_VALUES_IN_LOWER_BY_SURFACE_OUTPUTS, some)


_SURFACE_OUTPUTS_VALUES = tuple(t.value for t in SurfaceOutputs)
_SURFACE_OUTPUTS_VALUES_IN_LOWER_BY_SURFACE_OUTPUTS = {
    name.lower(): item for name, item in SurfaceOutputs.__members__.items()
}
