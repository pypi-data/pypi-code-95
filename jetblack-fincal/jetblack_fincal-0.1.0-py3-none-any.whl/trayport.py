"""
Trayport
"""


from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import (
    WEEKEND_CALENDAR,
    adjust,
    easter,
    add_nth_day_of_week,
    end_of_month,
    add_business_days,
    MonthOfYear,
    DayOfWeek,
    BusinessDayConvention,
    YearlyCalendar
)


class TrayportNBP(YearlyCalendar):
    """Trayport NBP"""

    def __init__(self) -> None:
        super().__init__(weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = date(year, 1, 1)
        holidays[
            adjust(
                new_years_day,
                BusinessDayConvention.FOLLOWING,
                cal=WEEKEND_CALENDAR
            )
        ] = "New Year's Day"

        easter_in_year = easter(year)
        holidays[easter_in_year - timedelta(2)] = "Good Friday"
        holidays[easter_in_year + timedelta(1)] = "Easter Monday"

        # May Day - first Monday in May.
        holidays[
            add_nth_day_of_week(
                date(year, MonthOfYear.MAY, 1),
                1,
                DayOfWeek.MONDAY,
                False
            )
        ] = "May Day"

        holidays[add_nth_day_of_week(end_of_month(year, MonthOfYear.AUGUST), -1, DayOfWeek.MONDAY,
                                     False)] = "August Bank Holiday"

        christmas_day = adjust(
            date(year, MonthOfYear.DECEMBER, 25),
            BusinessDayConvention.FOLLOWING, True,
            WEEKEND_CALENDAR
        )
        holidays[christmas_day] = "Christmas Day"
        holidays[add_business_days(
            christmas_day, 1, WEEKEND_CALENDAR)] = "Boxing Day"

        return holidays


class TrayportTTF(YearlyCalendar):
    """Trayport TTF"""

    def __init__(self) -> None:
        super().__init__(weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:

        holidays: Dict[date, str] = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_year = easter(year)
        easter_monday = easter_in_year + timedelta(days=1)
        holidays[easter_monday] = "Easter Monday"

        if year >= 1949 and year < 2014:
            # Queen's birthday
            queens_birthday = date(year, MonthOfYear.APRIL, 30)
            holidays[
                queens_birthday -
                timedelta(days=1) if queens_birthday.weekday(
                ) == DayOfWeek.SUNDAY else queens_birthday
            ] = "Queen's Birthday"

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


class TrayportNCG(YearlyCalendar):
    """Trayport NCG"""

    def __init__(self):
        super().__init__(weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:
        holidays = {}

        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[new_years_day] = "New Year's Day"

        easter_in_year = easter(year)
        easter_monday = easter_in_year + timedelta(days=1)
        holidays[easter_in_year - timedelta(2)] = "Good Friday"
        holidays[easter_monday] = "Easter Monday"

        holidays[date(year, MonthOfYear.MAY, 1)] = "Labour Day"

        holidays[easter_in_year + timedelta(days=39)] = "Ascension Day"

        holidays[add_nth_day_of_week(
            easter_monday, 7, DayOfWeek.MONDAY, True)] = "Whit Monday"

        holidays[date(year, MonthOfYear.OCTOBER, 3)] = "German Unity Day"

        if year == 2017:
            holidays[date(2017, MonthOfYear.OCTOBER, 31)
                     ] = "Day of Reformation"

        holidays[date(year, MonthOfYear.DECEMBER, 25)] = "Christmas Day"
        holidays[date(year, MonthOfYear.DECEMBER, 26)] = "Saint Stephens Day"

        return holidays
