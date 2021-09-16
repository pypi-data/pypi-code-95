# coding: utf8

__all__ = ["DayCountBasis"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class DayCountBasis(Enum):
    """
    The enum below values the various day count fraction methods.

    The possible values are:
        - Dcb_30E_360_ISMA - Actual number of days in the coupon period calculated on
            the basis of a year of 360 days with twelve 30-day months (regardless of
            the date of the first day or last day of the period).
        - Dcb_30_360 - Actual number of days in the coupon period calculated on the
            basis of a year of 360 days with twelve 30-day months unless:
                • the last day of the period is the 31st day of a month and the first
                    day of the period is a day other than the 30th or 31st day of a month,
                    in which case the month that includes the last day shall not be
                    considered to be shortened to a 30-day month.
                • the last day of the period is the last day of the month of February,
                    in which case the month of February shall not be considered to be
                    lengthened to a 30-day month.
        - Dcb_30_360_German - For two dates (Y1,M1,D1) and (Y2,M2,D2):
                • if D1=31 then D1=30
                • if D2=31 then D2=30
                • if D1 is the last day of February then D1=30
                • if D2 is the last day of February then D2=30
            The last day of February is February 29 in leap years and February 28 in
            non leap years.
            Then the date difference is (Y2-Y1)x360+(M2-M1)*30+(D2-D1).
        - Dcb_30_360_ISDA - For two dates (Y1,M1,D1) and (Y2,M2,D2):
                • if D1 is 31, change it to 30.
                • if D2 is 31 and D1 is 30, change D2 to 30.
            Then the date difference is (Y2-Y1)x360+(M2-M1)*30+(D2-D1).
        - Dcb_30_360_US - For two dates (Y1,M1,D1) and (Y2,M2,D2):
                • if D1=31 then D1=30
                • if D2=31 and D1=30 or 31 then D2=30
                • if D1 is the last day of February then D1=30
                • if D1 is the last day of February and D2 is the last day of February then D2=30
            The last day of February is February 29 in leap years and February 28 in
            non leap years.
            The 30/360 US rule is identical to 30/360 ISDA when the EOM (end-of-month)
            convention does not apply. This indicates whether all coupon payment dates
            fall on the last day of the month. If the investment is not EOM, it will
            always pay on the same day of the month (e.g., the 10th).
            Then the date difference is (Y2-Y1)x360+(M2-M1)*30+(D2-D1).
        - Dcb_30_365_Brazil - See details into `Developer Refinitiv Data Platform APIs <https://developers.refinitiv.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis/documentation#ipa-financial-contracts-day-conventions>`_
        - Dcb_30_365_German - Similar to 30/360 (German), except that the year basis is
            treated as 365 days.
        - Dcb_30_365_ISDA - For two dates (Y1,M1,D1) and (Y2,M2,D2):
                • if D1=31 then D1=30
                • if D2=31 and D1=30 or 31 then D2=30
            Then the date difference is (Y2-Y1)*360+(M2-M1)*30+(D2-D1).
        - Dcb_30_Actual - The day count is identical to 30/360 (US) and the year basis
            is identical to Actual/Actual.
        - Dcb_30_Actual_German - The day count is identical to 30/360 (German) and the
            year basis is similar to Actual/Actual. This method was formerly used in
            the Eurobond markets.
        - Dcb_30_Actual_ISDA - See details into `Developer Refinitiv Data Platform APIs <https://developers.refinitiv.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis/documentation#ipa-financial-contracts-day-conventions>`_
        - Dcb_ActualLeapDay_360 - The day count ignores 29th February when counting days.
            The year basis is 360 days.
        - Dcb_ActualLeapDay_365 - The day count ignores 29th February when counting days.
            The year basis is 365 days.
        - Dcb_Actual_360 - The day count is the actual number of days of the period.
            The year basis is 360.
        - Dcb_Actual_364 - A special case of Actual/Actual (ISMA) when a coupon period
            contains 91 or 182 days. Actual/364 applies for some short-term instruments.
            Day count basis = 364.
        - Dcb_Actual_365 - The day count is the actual number of days of the period.
            The year basis is 365.
        - Dcb_Actual_36525 - The day count is the actual number of days of the period.
            The year basis is 365.25.
        - Dcb_Actual_365L - The day count is the actual number of days of the period.
            The year basis is calculated in the following two rules:
                • if the coupon frequency is annual, then year basis is 366 if the 29 Feb.
                    is included in the interest period, else 365.
                • if the coupon frequency is not annual, then year basis is 366 for each
                    interest period where ending date falls in a leap year, otherwise it is 365.
        - Dcb_Actual_365P - See details into `Developer Refinitiv Data Platform APIs <https://developers.refinitiv.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis/documentation#ipa-financial-contracts-day-conventions>`_
        - Dcb_Actual_365_CanadianConvention - Follows the Canadian domestic bond market
            convention. The day count basis is computed as follows:
                • if the number of days of a period is less than the actual number of
                    days in a regular coupon period the Dcb_Actual_365 convention is used.
                • otherwise: DCB= 1 - DaysRemainingInPeriod x Frequency / 365.
        - Dcb_Actual_Actual - Similar to Actual/365, except for a period that includes
            days falling in a leap year. It is calculated by DCB = number of days in a
            leap year/366 + number of days in a non-leap year/365.
            A convention is also known as Actual/365 ISDA.
        - Dcb_Actual_Actual_AFB - The DCB is calculated by Actual days / year basis where:
                • Actual days is defined as the actual days between the start date
                    (D1.M1.Y1) and end date (D2.M2.Y2).
                • Year basis is either 365 if the calculation period does not contain
                    29th Feb, or 366 if the calculation period includes 29th Feb.
        - Dcb_Actual_Actual_ISDA - Similar to Actual/365, except for a period that
            includes days falling in a leap year. It is calculated by DCB = number of
            days in a leap year/366 + number of days in a non-leap year/365.
            A convention is also known as Actual/365 ISDA.
        - Dcb_Constant - See details into `Developer Refinitiv Data Platform APIs <https://developers.refinitiv.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis/documentation#ipa-financial-contracts-day-conventions>`_
        - Dcb_WorkingDays_252 - The day count is the actual number of business days of
            the period according to the instrument calendars. The year basis is 252.
            Commonly used in the Brazilian market.
    """

    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_CONSTANT = "Dcb_Constant"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DayCountBasis, _DAY_COUNT_BASIS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DAY_COUNT_BASIS_VALUES_IN_LOWER_BY_DAY_COUNT_BASIS, some)


_DAY_COUNT_BASIS_VALUES = tuple(t.value for t in DayCountBasis)
_DAY_COUNT_BASIS_VALUES_IN_LOWER_BY_DAY_COUNT_BASIS = {
    name.lower(): item for name, item in DayCountBasis.__members__.items()
}
