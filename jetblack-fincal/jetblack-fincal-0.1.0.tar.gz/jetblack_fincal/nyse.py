"""
NYSE Calendar
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import (
    WEEKEND_CALENDAR,
    add_nth_day_of_week,
    easter,
    end_of_month,
    nearest_business_day,
    DayOfWeek,
    MonthOfYear,
    YearlyCalendar
)


class NYSE(YearlyCalendar):
    """NYSE Calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

    def fetch_holidays(self, year: int) -> Dict[date, str]:

        holidays = {}

        # New Year's Day (possibly moved to Monday if on Sunday)
        new_years_day = date(year, MonthOfYear.JANUARY, 1)
        holidays[(
            new_years_day
            if new_years_day.weekday() != DayOfWeek.SUNDAY
            else new_years_day + timedelta(days=1))] = "New Year's Day"

        # Washington's birthday (third Monday in February)
        holidays[
            add_nth_day_of_week(
                date(year, MonthOfYear.FEBRUARY, 1),
                3,
                DayOfWeek.MONDAY,
                False
            )
        ] = "Washington's birthday"

        # Good Friday
        holidays[easter(year) + timedelta(days=1)] = "Good Friday"

        # Memorial Day (last Monday in May)
        holidays[add_nth_day_of_week(end_of_month(year, MonthOfYear.MAY), -1, DayOfWeek.MONDAY,
                                     False)] = "Memorial Day"

        # Independence Day (Monday if Sunday or Friday if Saturday)
        holidays[
            nearest_business_day(
                date(year, MonthOfYear.JULY, 4),
                True,
                WEEKEND_CALENDAR
            )] = "Independence Day"

        # Labor Day (first Monday in September)
        holidays[
            add_nth_day_of_week(date(year, MonthOfYear.SEPTEMBER, 1), 1, DayOfWeek.MONDAY,
                                False)] = "Labor Day"

        # Thanksgiving Day (fourth Thursday in November)
        holidays[add_nth_day_of_week(date(year, MonthOfYear.NOVEMBER, 1), 4, DayOfWeek.THURSDAY,
                                     False)] = "Thanksgiving"

        # Christmas (Monday if Sunday or Friday if Saturday)
        holidays[
            nearest_business_day(date(year, MonthOfYear.DECEMBER, 25), True,
                                 WEEKEND_CALENDAR)] = "Christmas Day"

        if year >= 1998:
            holidays[add_nth_day_of_week(date(year, MonthOfYear.JANUARY, 1), 3, DayOfWeek.MONDAY,
                                         False)] = "Martin Luther King's birthday"

        if year <= 1968 or (year <= 1980 and year % 4 == 0):
            holidays[add_nth_day_of_week(date(year, MonthOfYear.NOVEMBER, 1), 1, DayOfWeek.TUESDAY,
                                         True)] = "Presidential election days"

        # Special closings
        if year == 2012:
            holidays[date(2012, 10, 29)] = "Hurricane Sandy"
            holidays[date(2012, 10, 30)] = "Hurricane Sandy"

        if year == 2007:
            holidays[date(2007, 1, 2)] = "President Ford's funeral"

        if year == 2004:
            holidays[date(2004, 6, 11)] = "President Reagan's funeral"

        if year == 2001:
            holidays[date(2001, 9, 11)] = "9/11"
            holidays[date(2001, 9, 12)] = "9/11"
            holidays[date(2001, 9, 13)] = "9/11"
            holidays[date(2001, 9, 14)] = "9/11"

        if year == 1994:
            holidays[date(1994, 4, 27)] = "President Nixon's funeral"

        if year == 1985:
            holidays[date(1985, 9, 27)] = "Hurricane Gloria"

        if year == 1977:
            holidays[date(1977, 7, 14)] = "1977 Blackout"

        if year == 1973:
            holidays[date(1973, 1, 25)
                     ] = "Funeral of former President Lyndon B. Johnson."

        if year == 1972:
            holidays[date(1972, 12, 28)
                     ] = "Funeral of former President Harry S. Truman"

        if year == 1969:
            holidays[date(
                1969, 7, 21)] = "National Day of Participation for the lunar exploration."
            holidays[date(1969, 3, 31)
                     ] = "Funeral of former President Eisenhower."
            holidays[date(1969, 2, 10)] = "Closed all day - heavy snow."

        if year == 1968:
            holidays[date(1968, 7, 5)] = "Day after Independence Day."
            # June 12-Dec. 31, 1968
            # Four day week (closed on Wednesdays) - Paperwork Crisis
            hol = date(1968, 6, 12)
            while hol.year == 1968:
                holidays[hol] = "Paperwork Crisis"
                hol += timedelta(days=7)
            # Day of mourning for Martin Luther King Jr.
            holidays[date(1968, 4, 9)
                     ] = "Day of mourning for Martin Luther King Jr."

        if year == 1963:
            holidays[date(1963, 11, 25)] = "Funeral of President Kennedy"

        if year == 1961:
            holidays[date(1961, 5, 29)] = "Day before Decoration Day"

        if year == 1958:
            holidays[date(1958, 12, 26)] = "Day after Christmas"

        if year == 1954 or year == 1956 or year == 1965:
            holidays[date(year, 12, 24)] = "Christmas Eve"

        return holidays
