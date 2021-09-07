"""
Germany
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import (
    easter,
    add_nth_day_of_week,
    DayOfWeek,
    MonthOfYear,
    YearlyCalendar
)


class Germany(YearlyCalendar):
    """German calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_germany = easter(year)
        easter_monday = easter_in_germany + timedelta(days=1)
        holidays[easter_in_germany - timedelta(2)] = "Good Friday"
        holidays[easter_monday] = "Easter Monday"

        holidays[date(year, MonthOfYear.MAY, 1)] = "Labour Day"

        holidays[easter_in_germany + timedelta(days=39)] = "Ascension Day"

        holidays[add_nth_day_of_week(
            easter_monday, 7, DayOfWeek.MONDAY, True)] = "Whit Monday"

        holidays[date(year, MonthOfYear.OCTOBER, 3)] = "German Unity Day"

        if year == 2017:
            holidays[date(2017, MonthOfYear.OCTOBER, 31)
                     ] = "Day of Reformation"

        holidays[date(year, MonthOfYear.DECEMBER, 25)] = "Christmas Day"
        holidays[date(year, MonthOfYear.DECEMBER, 26)] = "Saint Stephens Day"

        return holidays
