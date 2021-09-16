# coding: utf8

__all__ = ["BusinessDayConvention"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class BusinessDayConvention(Enum):
    """
    The method to adjust dates to a working day.

    The possible values are:
        - BbswModifiedFollowing - dates are adjusted to the next business day convention
            unless is it goes into the next month, or crosses mid-month (15th).
            In this case, the Previous Business Day convention is used.
        - EveryThirdWednesday - dates are adjusted to the next every third Wednesday.
        - ModifiedFollowing - dates are adjusted to the next business day convention
            unless is it goes into the next month. In this case, the Previous Business
            Day convention is used.
        - NextBusinessDay - dates are moved to the following working day.
        - NoMoving - dates are not adjusted.
        - PreviousBusinessDay - dates are moved to the preceding working day.
    """

    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    MODIFIED_FOLLOWING = "ModifiedFollowing"
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    NO_MOVING = "NoMoving"
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BusinessDayConvention, _CONVENTION_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_CONVENTION_VALUES_IN_LOWER_BY_CONVENTION, some)


_CONVENTION_VALUES = tuple(t.value for t in BusinessDayConvention)
_CONVENTION_VALUES_IN_LOWER_BY_CONVENTION = {
    name.lower(): item for name, item in BusinessDayConvention.__members__.items()
}
