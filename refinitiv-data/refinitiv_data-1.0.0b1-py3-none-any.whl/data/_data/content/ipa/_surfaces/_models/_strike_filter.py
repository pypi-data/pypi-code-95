# coding: utf8

__all__ = ["StrikeFilter"]

from ..._object_definition import ObjectDefinition


class StrikeFilter(ObjectDefinition):
    def __init__(self, max_of_median_implied_vol=None, min_of_median_implied_vol=None):
        super().__init__()
        self.max_of_median_implied_vol = max_of_median_implied_vol
        self.min_of_median_implied_vol = min_of_median_implied_vol

    @property
    def max_of_median_implied_vol(self):
        """
        Remove strikes whose implied vol is more than MaxOfMedianImpliedVolPercent x Median implied Vol.
        :return: float
        """
        return self._get_parameter("maxOfMedianImpliedVol")

    @max_of_median_implied_vol.setter
    def max_of_median_implied_vol(self, value):
        self._set_parameter("maxOfMedianImpliedVol", value)

    @property
    def min_of_median_implied_vol(self):
        """
        Remove strikes whose implied vol is less than MinOfMedianImpliedVolPercent x Median implied Vol.
        :return: float
        """
        return self._get_parameter("minOfMedianImpliedVol")

    @min_of_median_implied_vol.setter
    def min_of_median_implied_vol(self, value):
        self._set_parameter("minOfMedianImpliedVol", value)
