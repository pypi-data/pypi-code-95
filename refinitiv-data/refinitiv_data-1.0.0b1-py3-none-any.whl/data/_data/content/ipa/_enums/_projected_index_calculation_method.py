# coding: utf8
# contract_gen 2020-05-18 08:30:59.209815

__all__ = ["ProjectedIndexCalculationMethod"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class ProjectedIndexCalculationMethod(Enum):
    """
    Flag used to define how projected index is computed.

    Avalaible values are:
    - "ConstantIndex" : future index values are considered as constant and equal to
      projected index value.
    - "ForwardIndex" : future index values are computed using a forward curve.
    """

    CONSTANT_INDEX = "ConstantIndex"
    FORWARD_INDEX = "ForwardIndex"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            ProjectedIndexCalculationMethod,
            _PROJECTED_INDEX_CALCULATION_METHOD_VALUES,
            some,
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _PROJECTED_INDEX_CALCULATION_METHOD_VALUES_IN_LOWER_BY_PROJECTED_INDEX_CALCULATION_METHOD,
            some,
        )


_PROJECTED_INDEX_CALCULATION_METHOD_VALUES = tuple(
    t.value for t in ProjectedIndexCalculationMethod
)
_PROJECTED_INDEX_CALCULATION_METHOD_VALUES_IN_LOWER_BY_PROJECTED_INDEX_CALCULATION_METHOD = {
    name.lower(): item
    for name, item in ProjectedIndexCalculationMethod.__members__.items()
}
