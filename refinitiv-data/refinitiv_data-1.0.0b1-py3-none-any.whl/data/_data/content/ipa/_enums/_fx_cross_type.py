# coding: utf8

__all__ = ["FxCrossType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class FxCrossType(Enum):
    """
    The type of the Fx Cross instrument :
        'FxSpot',
        'FxForward',
        'FxNonDeliverableForward',
        'FxSwap',
        'MultiLeg' or 'FxForwardForward'.
    """

    FX_FORWARD = "FxForward"
    FX_FWD_FWD = "FxFwdFwd"
    FX_NON_DELIVERABLE_FORWARD = "FxNonDeliverableForward"
    FX_SPOT = "FxSpot"
    FX_SWAP = "FxSwap"
    FX_TIME_OPTION_FORWARD = "FxTimeOptionForward"
    MULTI_LEG = "MultiLeg"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FxCrossType, _FX_CROSS_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FX_CROSS_TYPE_VALUES_IN_LOWER_BY_FX_CROSS_TYPE, some)


_FX_CROSS_TYPE_VALUES = tuple(t.value for t in FxCrossType)
_FX_CROSS_TYPE_VALUES_IN_LOWER_BY_FX_CROSS_TYPE = {
    name.lower(): item for name, item in FxCrossType.__members__.items()
}
