# coding: utf8

__all__ = ["MaturityFilter"]

from ..._object_definition import ObjectDefinition


class MaturityFilter(ObjectDefinition):
    def __init__(
        self,
        max_maturity=None,
        min_maturity=None,
        min_of_median_nb_of_strikes_percent=None,
    ):
        super().__init__()
        self.max_maturity = max_maturity
        self.min_maturity = min_maturity
        self.min_of_median_nb_of_strikes_percent = min_of_median_nb_of_strikes_percent

    @property
    def max_maturity(self):
        """
        Max Maturity to consider in the filtering. (expressed in tenor)
        :return: str
        """
        return self._get_parameter("maxMaturity")

    @max_maturity.setter
    def max_maturity(self, value):
        self._set_parameter("maxMaturity", value)

    @property
    def min_maturity(self):
        """
        Min Maturity to consider in the filtering. (expressed in tenor)
        Default value: 7D
        :return: str
        """
        return self._get_parameter("minMaturity")

    @min_maturity.setter
    def min_maturity(self, value):
        self._set_parameter("minMaturity", value)

    @property
    def min_of_median_nb_of_strikes_percent(self):
        """
        Remove maturities whose number of strikes is less than MinOfMedianNbOfStrikesPercent of the Median number of Strikes.
        :return: float
        """
        return self._get_parameter("minOfMedianNbOfStrikesPercent")

    @min_of_median_nb_of_strikes_percent.setter
    def min_of_median_nb_of_strikes_percent(self, value):
        self._set_parameter("minOfMedianNbOfStrikesPercent", value)
