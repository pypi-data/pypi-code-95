# coding: utf8

__all__ = ["BenchmarkYieldSelectionMode"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class BenchmarkYieldSelectionMode(Enum):
    """
    The benchmark yield selection mode:
        - Interpolate : do an interpolatation on yield curve to compute the reference
          yield.
        - Nearest : use the nearest point to find the reference yield.
    """

    INTERPOLATE = "Interpolate"
    NEAREST = "Nearest"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            BenchmarkYieldSelectionMode, _BENCHMARK_YIELD_SELECTION_MODE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _BENCHMARK_YIELD_SELECTION_MODE_VALUES_IN_LOWER_BY_BENCHMARK_YIELD_SELECTION_MODE,
            some,
        )


_BENCHMARK_YIELD_SELECTION_MODE_VALUES = tuple(
    t.value for t in BenchmarkYieldSelectionMode
)
_BENCHMARK_YIELD_SELECTION_MODE_VALUES_IN_LOWER_BY_BENCHMARK_YIELD_SELECTION_MODE = {
    name.lower(): item for name, item in BenchmarkYieldSelectionMode.__members__.items()
}
