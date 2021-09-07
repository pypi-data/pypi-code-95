"""
Target
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import easter, DayOfWeek, YearlyCalendar


class Target(YearlyCalendar):
    """Target Calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:

        holidays = {}

        new_years_day = date(year, 1, 1)
        holidays[new_years_day] = "New Year's Day"

        if year >= 2000:
            easter_sunday = easter(year)
            holidays[easter_sunday - timedelta(2)] = "Good Friday"
            holidays[easter_sunday + timedelta(1)] = "Easter Monday"

        if year >= 2000:
            holidays[date(year, 5, 1)] = "Labour Day"

        holidays[date(year, 12, 25)] = "Christmas Day"

        if year >= 2000:
            holidays[date(year, 12, 26)] = "Christmas Holiday"

        if year == 1998 or year == 1999 or year == 2001:
            holidays[date(year, 12, 31)] = "New Years Eve"

        return holidays
