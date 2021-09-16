# coding: utf8

__all__ = ["ForwardCurvesOutputs"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class ForwardCurvesOutputs(Enum):
    CONSTITUENTS = "Constituents"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            ForwardCurvesOutputs, _FORWARD_CURVES_OUTPUTS_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _FORWARD_CURVES_OUTPUTS_VALUES_IN_LOWER_BY_FORWARD_CURVES_OUTPUTS, some
        )


_FORWARD_CURVES_OUTPUTS_VALUES = tuple(t.value for t in ForwardCurvesOutputs)
_FORWARD_CURVES_OUTPUTS_VALUES_IN_LOWER_BY_FORWARD_CURVES_OUTPUTS = {
    name.lower(): item for name, item in ForwardCurvesOutputs.__members__.items()
}
