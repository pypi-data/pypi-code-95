# coding: utf8

__all__ = ["IndexSpreadCompoundingMethod"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class IndexSpreadCompoundingMethod(Enum):
    ISDA_COMPOUNDING = "IsdaCompounding"
    ISDA_FLAT_COMPOUNDING = "IsdaFlatCompounding"
    NO_COMPOUNDING = "NoCompounding"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            IndexSpreadCompoundingMethod, _INDEX_SPREAD_COMPOUNDING_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _INDEX_SPREAD_COMPOUNDING_METHOD_VALUES_IN_LOWER_BY_INDEX_SPREAD_COMPOUNDING_METHOD,
            some,
        )


_INDEX_SPREAD_COMPOUNDING_METHOD_VALUES = tuple(
    t.value for t in IndexSpreadCompoundingMethod
)
_INDEX_SPREAD_COMPOUNDING_METHOD_VALUES_IN_LOWER_BY_INDEX_SPREAD_COMPOUNDING_METHOD = {
    name.lower(): item
    for name, item in IndexSpreadCompoundingMethod.__members__.items()
}
