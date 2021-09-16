# coding: utf8

__all__ = ["FxAverageInfo"]

from typing import Optional

from .._base import Info
from .._enums import (
    AverageType,
    FixingFrequency,
)


class FxAverageInfo(Info):
    """
    Parameters
    ----------
    average_type : AverageType, optional
        The type of average used to compute. Possible values:
        - ArithmeticRate
        - ArithmeticStrike
        - GeometricRate
        - GeometricStrike
    fixing_frequency : FixingFrequency, optional
        The fixing's frequency. Possible values:
        - Daily
        - Weekly
        - BiWeekly
        - Monthly
        - Quaterly
        - SemiAnnual
        - Annual
    average_so_far : float, optional
        The value of the average_type
    fixing_ric_source : str, optional
        The fixing's RIC source. Default value: the first available source RIC of the Fx
        Cross Code
    fixing_start_date : str, optional
        The beginning date of the fixing period.
    include_holidays : bool, optional
        Include the holidays in the list of fixings
    include_week_ends : bool, optional
        Include the week-ends in the list of fixings
    """

    def __init__(
        self,
        average_type: Optional[AverageType] = None,
        fixing_frequency: Optional[FixingFrequency] = None,
        average_so_far: Optional[float] = None,
        fixing_ric_source: Optional[str] = None,
        fixing_start_date: Optional[str] = None,
        include_holidays: Optional[bool] = None,
        include_week_ends: Optional[bool] = None,
    ) -> None:
        super().__init__()
        self.average_type = average_type
        self.fixing_frequency = fixing_frequency
        self.average_so_far = average_so_far
        self.fixing_ric_source = fixing_ric_source
        self.fixing_start_date = fixing_start_date
        self.include_holidays = include_holidays
        self.include_week_ends = include_week_ends

    @property
    def average_type(self):
        """
        The type of average used to compute. Possible values:
        - ArithmeticRate
        - ArithmeticStrike
        - GeometricRate
        - GeometricStrike
        :return: enum AverageType
        """
        return self._get_enum_parameter(AverageType, "averageType")

    @average_type.setter
    def average_type(self, value):
        self._set_enum_parameter(AverageType, "averageType", value)

    @property
    def fixing_frequency(self):
        """
        The fixing's frequency. Possible values:
        - Daily
        - Weekly
        - BiWeekly
        - Monthly
        - Quaterly
        - SemiAnnual
        - Annual
        :return: enum FixingFrequency
        """
        return self._get_enum_parameter(FixingFrequency, "fixingFrequency")

    @fixing_frequency.setter
    def fixing_frequency(self, value):
        self._set_enum_parameter(FixingFrequency, "fixingFrequency", value)

    @property
    def average_so_far(self):
        """
        The value of the average_type
        :return: float
        """
        return self._get_parameter("averageSoFar")

    @average_so_far.setter
    def average_so_far(self, value):
        self._set_parameter("averageSoFar", value)

    @property
    def fixing_ric_source(self):
        """
        The fixing's RIC source. Default value: the first available source RIC of the Fx
        Cross Code
        :return: str
        """
        return self._get_parameter("fixingRicSource")

    @fixing_ric_source.setter
    def fixing_ric_source(self, value):
        self._set_parameter("fixingRicSource", value)

    @property
    def fixing_start_date(self):
        """
        The beginning date of the fixing period.
        :return: str
        """
        return self._get_parameter("fixingStartDate")

    @fixing_start_date.setter
    def fixing_start_date(self, value):
        self._set_parameter("fixingStartDate", value)

    @property
    def include_holidays(self):
        """
        Include the holidays in the list of fixings
        :return: bool
        """
        return self._get_parameter("includeHolidays")

    @include_holidays.setter
    def include_holidays(self, value):
        self._set_parameter("includeHolidays", value)

    @property
    def include_week_ends(self):
        """
        Include the week-ends in the list of fixings
        :return: bool
        """
        return self._get_parameter("includeWeekEnds")

    @include_week_ends.setter
    def include_week_ends(self, value):
        self._set_parameter("includeWeekEnds", value)
