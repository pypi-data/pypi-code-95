"""
Netherlands Calendar
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


class Netherlands(YearlyCalendar):
    """Netherlands calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:

        holidays = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_year = easter(year)
        easter_monday = easter_in_year + timedelta(days=1)
        holidays[easter_monday] = "Easter Monday"

        if year >= 1949 and year < 2014:
            # Queen's birthday
            queens_birthday = date(year, MonthOfYear.APRIL, 30)
            holidays[queens_birthday -
                     timedelta(days=1)
                     if queens_birthday.weekday() == DayOfWeek.SUNDAY
                     else queens_birthday] = "Queen's Birthday"

        if year >= 2014:
            # Kings birthday
            kings_birthday = date(year, MonthOfYear.APRIL, 27)
            holidays[kings_birthday -
                     timedelta(days=1)
                     if kings_birthday.weekday() == DayOfWeek.SUNDAY
                     else kings_birthday] = "King's Birthday"

        holidays[easter_in_year + timedelta(days=39)] = "Ascension Day"

        holidays[easter_in_year + timedelta(days=49)] = "Pentecost Sunday"

        holidays[add_nth_day_of_week(
            easter_monday, 7, DayOfWeek.MONDAY, True)] = "Whit Monday"

        holidays[date(year, MonthOfYear.DECEMBER, 25)] = "Christmas Day"
        holidays[date(year, MonthOfYear.DECEMBER, 26)] = "Saint Stephens Day"

        return holidays
