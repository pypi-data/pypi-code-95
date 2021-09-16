# coding: utf8

__all__ = ["FxLegType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class FxLegType(Enum):
    """
    The enumeration that specifies the type of the leg :
        'Spot',
        'FxForward',
        'FxNonDeliverableForward',
        'SwapNear' or 'SwapFar'.
    Mandatory for MultiLeg, FwdFwdSwap, or Swap contracts.
    Optional for Spot and Forwards contracts.
    """

    FX_FORWARD = "FxForward"
    FX_NON_DELIVERABLE_FORWARD = "FxNonDeliverableForward"
    FX_SPOT = "FxSpot"
    SWAP_FAR = "SwapFar"
    SWAP_NEAR = "SwapNear"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FxLegType, _FX_LEG_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FX_LEG_TYPE_VALUES_IN_LOWER_BY_FX_LEG_TYPE, some)


_FX_LEG_TYPE_VALUES = tuple(t.value for t in FxLegType)
_FX_LEG_TYPE_VALUES_IN_LOWER_BY_FX_LEG_TYPE = {
    name.lower(): item for name, item in FxLegType.__members__.items()
}
