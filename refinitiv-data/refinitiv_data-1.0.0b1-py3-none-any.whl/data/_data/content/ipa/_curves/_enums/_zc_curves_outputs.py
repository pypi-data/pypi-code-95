# coding: utf8

__all__ = ["ZcCurvesOutputs"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class ZcCurvesOutputs(Enum):
    CONSTITUENTS = "Constituents"
    DETAILED_CURVE_POINT = "DetailedCurvePoint"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(ZcCurvesOutputs, _ZC_CURVES_OUTPUTS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_ZC_CURVES_OUTPUTS_VALUES_IN_LOWER_BY_ZC_CURVES_OUTPUTS, some)


_ZC_CURVES_OUTPUTS_VALUES = tuple(t.value for t in ZcCurvesOutputs)
_ZC_CURVES_OUTPUTS_VALUES_IN_LOWER_BY_ZC_CURVES_OUTPUTS = {
    name.lower(): item for name, item in ZcCurvesOutputs.__members__.items()
}
