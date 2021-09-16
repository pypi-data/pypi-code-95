# coding: utf8

__all__ = ["ZcInterpolationMode"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class ZcInterpolationMode(Enum):
    AKIMA_METHOD = "AkimaMethod"
    CUBIC_DISCOUNT = "CubicDiscount"
    CUBIC_RATE = "CubicRate"
    CUBIC_SPLINE = "CubicSpline"
    FORWARD_MONOTONE_CONVEX = "ForwardMonotoneConvex"
    FRITSCH_BUTLAND_METHOD = "FritschButlandMethod"
    HERMITE = "Hermite"
    KRUGER_METHOD = "KrugerMethod"
    LINEAR = "Linear"
    LOG = "Log"
    MONOTONIC_CUBIC_NATURAL_SPLINE = "MonotonicCubicNaturalSpline"
    MONOTONIC_HERMITE_CUBIC = "MonotonicHermiteCubic"
    TENSION_SPLINE = "TensionSpline"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(ZcInterpolationMode, _ZC_INTERPOLATION_MODE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _ZC_INTERPOLATION_MODE_VALUES_IN_LOWER_BY_ZC_INTERPOLATION_MODE, some
        )


_ZC_INTERPOLATION_MODE_VALUES = tuple(t.value for t in ZcInterpolationMode)
_ZC_INTERPOLATION_MODE_VALUES_IN_LOWER_BY_ZC_INTERPOLATION_MODE = {
    name.lower(): item for name, item in ZcInterpolationMode.__members__.items()
}
