"""
ICE Calendar
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import (
    DayOfWeek,
    YearlyCalendar,
    BusinessDayConvention,
    WEEKEND_CALENDAR,
    adjust,
    easter,
    MonthOfYear
)


class IceEurope(YearlyCalendar):
    """ICE Europe"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = adjust(
            date(year, 1, 1), BusinessDayConvention.FOLLOWING, cal=WEEKEND_CALENDAR)
        holidays[new_years_day] = "New Year's Day"

        holidays[easter(year) - timedelta(2)] = "Good Friday"

        christmas_day = adjust(
            date(year, 12, 25), BusinessDayConvention.FOLLOWING, cal=WEEKEND_CALENDAR)
        holidays[christmas_day] = "Christmas Day"

        return holidays


class IceUS(YearlyCalendar):
    """ICE US"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = adjust(
            date(year, MonthOfYear.JANUARY, 1),
            BusinessDayConvention.FOLLOWING,
            cal=WEEKEND_CALENDAR)
        holidays[new_years_day] = "New Year's Day"

        holidays[easter(year) - timedelta(2)] = "Good Friday"

        christmas_day = adjust(
            date(year, MonthOfYear.DECEMBER, 25),
            BusinessDayConvention.FOLLOWING,
            cal=WEEKEND_CALENDAR)
        holidays[christmas_day] = "Christmas Day"

        return holidays
