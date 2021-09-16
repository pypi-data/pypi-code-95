# coding: utf8

__all__ = ["StrikeFilterRange"]

from ..._object_definition import ObjectDefinition


class StrikeFilterRange(ObjectDefinition):
    def __init__(
        self,
        max_of_median_implied_vol_percent=None,
        min_of_median_implied_vol_percent=None,
    ):
        super().__init__()
        self.max_of_median_implied_vol_percent = max_of_median_implied_vol_percent
        self.min_of_median_implied_vol_percent = min_of_median_implied_vol_percent

    @property
    def max_of_median_implied_vol_percent(self):
        """
        Remove strikes whose implied vol is more than MaxOfMedianImpliedVolPercent x Median implied Vol.
        :return: float
        """
        return self._get_parameter("maxOfMedianImpliedVolPercent")

    @max_of_median_implied_vol_percent.setter
    def max_of_median_implied_vol_percent(self, value):
        self._set_parameter("maxOfMedianImpliedVolPercent", value)

    @property
    def min_of_median_implied_vol_percent(self):
        """
        Remove strikes whose implied vol is less than MinOfMedianImpliedVolPercent x Median implied Vol.
        :return: float
        """
        return self._get_parameter("minOfMedianImpliedVolPercent")

    @min_of_median_implied_vol_percent.setter
    def min_of_median_implied_vol_percent(self, value):
        self._set_parameter("minOfMedianImpliedVolPercent", value)
