# coding: utf8

__all__ = ["Turn"]

from .._forward_curve_types import OptInt, OptFloat
from ..._object_definition import ObjectDefinition


class Turn(ObjectDefinition):
    """
    Parameters
    ----------
    month : int, optional
        Month of the turn period
    rate_percent : float, optional
        Turn rate expressed in percents
    year : int, optional
        Year of the turn period
    """

    def __init__(
        self,
        month: OptInt = None,
        rate_percent: OptFloat = None,
        year: OptInt = None,
    ) -> None:
        super().__init__()
        self.month = month
        self.rate_percent = rate_percent
        self.year = year

    @property
    def month(self):
        """
        Month of the turn period
        :return: int
        """
        return self._get_parameter("month")

    @month.setter
    def month(self, value):
        self._set_parameter("month", value)

    @property
    def rate_percent(self):
        """
        Turn rate expressed in percents
        :return: float
        """
        return self._get_parameter("ratePercent")

    @rate_percent.setter
    def rate_percent(self, value):
        self._set_parameter("ratePercent", value)

    @property
    def year(self):
        """
        Year of the turn period
        :return: int
        """
        return self._get_parameter("year")

    @year.setter
    def year(self, value):
        self._set_parameter("year", value)
