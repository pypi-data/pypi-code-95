"""
Belgium
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import easter, DayOfWeek, MonthOfYear, YearlyCalendar


class Belgium(YearlyCalendar):
    """Belgium Calendar"""

    def __init__(self):
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_belgium = easter(year)
        easter_monday = easter_in_belgium + timedelta(days=1)
        holidays[easter_monday] = "Easter Monday"

        holidays[date(year, MonthOfYear.MAY, 1)] = "Labour Day"

        holidays[easter_in_belgium + timedelta(days=39)] = "Ascension Day"

        holidays[easter_in_belgium + timedelta(days=50)] = "Pentecost Monday"

        holidays[date(year, MonthOfYear.JULY, 21)] = "Belgium National Day"

        holidays[date(year, MonthOfYear.AUGUST, 15)] = "Assumption of Mary"

        holidays[date(year, MonthOfYear.NOVEMBER, 1)] = "All Saints Day"

        holidays[date(year, MonthOfYear.NOVEMBER, 11)] = "Armistice Day"

        holidays[date(year, MonthOfYear.DECEMBER, 25)] = "Christmas Day"

        return holidays


class EuropeanInstitutions(YearlyCalendar):
    """European Institution calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_belgium = easter(year)
        easter_monday = easter_in_belgium + timedelta(days=1)
        holidays[easter_monday] = "Easter Monday"

        holidays[date(year, MonthOfYear.MAY, 1)] = "Labour Day"

        holidays[date(year, MonthOfYear.MAY, 9)] = "Schuman Day"

        holidays[easter_in_belgium + timedelta(days=39)] = "Ascension Day"

        holidays[easter_in_belgium + timedelta(days=50)] = "Pentecost Monday"

        holidays[date(year, MonthOfYear.JULY, 21)] = "Belgium National Day"

        holidays[date(year, MonthOfYear.AUGUST, 15)] = "Assumption of Mary"

        holidays[date(year, MonthOfYear.NOVEMBER, 1)] = "All Saints Day"

        holidays[date(year, MonthOfYear.DECEMBER, 25)] = "Christmas Day"

        return holidays
