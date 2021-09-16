# coding: utf8

__all__ = ["InterpolationWeight"]

from typing import Optional, Iterable

from .._object_definition import ObjectDefinition
from .._models import DayWeight


class InterpolationWeight(ObjectDefinition):
    """
    Parameters
    ----------
    days_list : list of DayWeight, optional

    holidays : float, optional

    week_days : float, optional

    week_ends : float, optional

    """

    def __init__(
        self,
        days_list: Optional[Iterable[DayWeight]] = None,
        holidays: Optional[float] = None,
        week_days: Optional[float] = None,
        week_ends: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.days_list = days_list
        self.holidays = holidays
        self.week_days = week_days
        self.week_ends = week_ends

    @property
    def days_list(self):
        """
        :return: list DayWeight
        """
        return self._get_list_parameter(DayWeight, "daysList")

    @days_list.setter
    def days_list(self, value):
        self._set_list_parameter(DayWeight, "daysList", value)

    @property
    def holidays(self):
        """
        :return: float
        """
        return self._get_parameter("holidays")

    @holidays.setter
    def holidays(self, value):
        self._set_parameter("holidays", value)

    @property
    def week_days(self):
        """
        :return: float
        """
        return self._get_parameter("weekDays")

    @week_days.setter
    def week_days(self, value):
        self._set_parameter("weekDays", value)

    @property
    def week_ends(self):
        """
        :return: float
        """
        return self._get_parameter("weekEnds")

    @week_ends.setter
    def week_ends(self, value):
        self._set_parameter("weekEnds", value)
