import enum


@enum.unique
class EnumQuoteEventType(enum.Enum):
    on_start = 0
    on_end = 1
    on_bar = 2
    on_tick = 3
    on_day_begin = 4
    on_day_end = 5