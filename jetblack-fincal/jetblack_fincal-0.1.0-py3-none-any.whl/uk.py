"""
UK Calendar
"""

from datetime import timedelta, date
from typing import Dict

from jetblack_datemath import (
    WEEKEND_CALENDAR,
    adjust,
    add_nth_day_of_week,
    easter,
    end_of_month,
    add_business_days,
    DayOfWeek,
    MonthOfYear,
    BusinessDayConvention,
    YearlyCalendar
)


class UK(YearlyCalendar):
    """UK Calendar"""

    def __init__(self) -> None:
        YearlyCalendar.__init__(
            self,
            weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]
        )

    def fetch_holidays(self, year: int) -> Dict[date, str]:

        holidays = {}

        # New Years Days, adjusted to the first non-weekend.
        new_years_day = adjust(
            date(year, MonthOfYear.JANUARY, 1),
            BusinessDayConvention.FOLLOWING,
            True,
            WEEKEND_CALENDAR)
        holidays[new_years_day] = "New Years Days"

        # Good Friday and Easter Monday
        easter_in_year = easter(year)
        holidays[easter_in_year - timedelta(2)] = "Good Friday"
        holidays[easter_in_year + timedelta(1)] = "Easter Monday"

        if year == 2011:
            holidays[date(2011, MonthOfYear.APRIL, 29)] = "Royal Wedding"

        # May Day - first Monday in May.
        may_day = add_nth_day_of_week(
            date(year, MonthOfYear.MAY, 1), 1, DayOfWeek.MONDAY, False)
        holidays[may_day] = "May Day"

        if year == 2002:
            holidays[date(2002, MonthOfYear.JUNE, 3)
                     ] = "Golden Jubilee Bank Holiday"
            holidays[date(2002, MonthOfYear.JUNE, 4)
                     ] = "Special Spring Bank Holiday"
        elif year == 2012:
            holidays[date(2012, MonthOfYear.JUNE, 4)
                     ] = "Diamond Jubilee Bank Holiday"
            holidays[date(2012, MonthOfYear.JUNE, 5)
                     ] = "Special Spring Bank Holiday"
        else:
            spring_bank_holiday = add_nth_day_of_week(
                end_of_month(year, MonthOfYear.MAY),
                -1,
                DayOfWeek.MONDAY,
                False)
            holidays[spring_bank_holiday] = "Spring Bank Holiday - last Monday in May"

        august_bank_holiday = add_nth_day_of_week(
            end_of_month(year, MonthOfYear.AUGUST),
            -1,
            DayOfWeek.MONDAY,
            False)
        holidays[august_bank_holiday] = "August Bank Holiday - last Monday in August."

        christmas_day = adjust(
            date(year, MonthOfYear.DECEMBER, 25),
            BusinessDayConvention.FOLLOWING,
            True,
            WEEKEND_CALENDAR)
        holidays[christmas_day] = "Christmas Day"

        holidays[add_business_days(
            christmas_day, 1, WEEKEND_CALENDAR)] = "Boxing Day"

        if year == 1999:
            holidays[date(1999, MonthOfYear.DECEMBER, 31)
                     ] = "Millennium Celebration"

        return holidays
