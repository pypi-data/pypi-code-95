# coding: utf8

__all__ = ["Frequency"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class Frequency(Enum):
    """
    The time frequency
    """

    EVERYDAY = "Everyday"
    BI_MONTHLY = "BiMonthly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    SEMI_ANNUAL = "SemiAnnual"
    ANNUAL = "Annual"
    EVERY7_DAYS = "Every7Days"
    EVERY14_DAYS = "Every14Days"
    EVERY28_DAYS = "Every28Days"
    EVERY30_DAYS = "Every30Days"
    EVERY91_DAYS = "Every91Days"
    EVERY182_DAYS = "Every182Days"
    EVERY364_DAYS = "Every364Days"
    EVERY365_DAYS = "Every365Days"
    EVERY90_DAYS = "Every90Days"
    EVERY92_DAYS = "Every92Days"
    EVERY93_DAYS = "Every93Days"
    EVERY180_DAYS = "Every180Days"
    EVERY183_DAYS = "Every183Days"
    EVERY184_DAYS = "Every184Days"
    EVERY4_MONTHS = "Every4Months"
    EVERY_WORKING_DAY = "EveryWorkingDay"
    R2 = "R2"
    R4 = "R4"
    SCHEDULED = "Scheduled"
    ZERO = "Zero"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Frequency, _FREQUENCY_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FREQUENCY_VALUES_IN_LOWER_BY_FREQUENCY, some)


_FREQUENCY_VALUES = tuple(t.value for t in Frequency)
_FREQUENCY_VALUES_IN_LOWER_BY_FREQUENCY = {
    name.lower(): item for name, item in Frequency.__members__.items()
}
