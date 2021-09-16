# coding: utf8
# contract_gen 2020-05-18 08:30:59.202852

__all__ = ["IndexCompoundingMethod"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class IndexCompoundingMethod(Enum):
    """
    A flag that defines how the coupon rate is calculated from the reset floating
    rates when the reset frequency is higher than the interest payment frequency
    (e.g. daily index reset with quarterly interest payment).

    The possible values are:
        - Compounded (uses the compounded average rate from multiple fixings),
        - Average (uses the arithmetic average rate from multiple fixings),
        - Constant (uses the last published rate among multiple fixings),
        - AdjustedCompounded (uses Chinese 7-day repo fixing),
        - MexicanCompounded (uses Mexican Bremse fixing).
    """

    ADJUSTED_COMPOUNDED = "AdjustedCompounded"
    AVERAGE = "Average"
    COMPOUNDED = "Compounded"
    CONSTANT = "Constant"
    MEXICAN_COMPOUNDED = "MexicanCompounded"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            IndexCompoundingMethod, _INDEX_COMPOUNDING_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _INDEX_COMPOUNDING_METHOD_VALUES_IN_LOWER_BY_INDEX_COMPOUNDING_METHOD, some
        )


_INDEX_COMPOUNDING_METHOD_VALUES = tuple(t.value for t in IndexCompoundingMethod)
_INDEX_COMPOUNDING_METHOD_VALUES_IN_LOWER_BY_INDEX_COMPOUNDING_METHOD = {
    name.lower(): item for name, item in IndexCompoundingMethod.__members__.items()
}
