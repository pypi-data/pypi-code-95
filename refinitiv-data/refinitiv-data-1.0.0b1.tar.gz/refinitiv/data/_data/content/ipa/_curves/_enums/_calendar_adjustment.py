# coding: utf8

__all__ = ["CalendarAdjustment"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class CalendarAdjustment(Enum):
    FALSE = False
    NULL = None
    WEEKEND = "Weekend"
    CALENDAR = "Calendar"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CalendarAdjustment, _CALENDAR_ADJUSTMENT_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _CALENDAR_ADJUSTMENT_VALUES_IN_LOWER_BY_CALENDAR_ADJUSTMENT, some
        )


_CALENDAR_ADJUSTMENT_VALUES = tuple(t.value for t in CalendarAdjustment)
_CALENDAR_ADJUSTMENT_VALUES_IN_LOWER_BY_CALENDAR_ADJUSTMENT = {
    name.lower(): item for name, item in CalendarAdjustment.__members__.items()
}
