import enum


@enum.unique
class EnumTradeEventType(enum.Enum):
    on_order = 0
    on_trade = 1
    on_order_reject = 2
    on_order_cancel_failed = 3
    on_order_canceled = 4
