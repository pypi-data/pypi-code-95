# coding: utf8

__all__ = ["DateRollingConvention"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class DateRollingConvention(Enum):
    """
    Method to adjust payment dates when they fall at the end of the month (28th of
    February, 30th, 31st).

    The possible values are:
        - Last (For setting the calculated date to the last working day),
        - Same (For setting the calculated date to the same day . In this latter case,
            the date may be moved according to the date moving convention if it is
            a non-working day),
        - Last28 (For setting the calculated date to the last working day. 28FEB being
            always considered as the last working day),
        - Same28 (For setting the calculated date to the same day .28FEB being always
            considered as the last working day).
    """

    LAST = "Last"
    LAST28 = "Last28"
    SAME = "Same"
    SAME28 = "Same28"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            DateRollingConvention, _PAYMENT_ROLL_CONVENTION_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _PAYMENT_ROLL_CONVENTION_VALUES_IN_LOWER_BY_PAYMENT_ROLL_CONVENTION, some
        )


_PAYMENT_ROLL_CONVENTION_VALUES = tuple(t.value for t in DateRollingConvention)
_PAYMENT_ROLL_CONVENTION_VALUES_IN_LOWER_BY_PAYMENT_ROLL_CONVENTION = {
    name.lower(): item for name, item in DateRollingConvention.__members__.items()
}
