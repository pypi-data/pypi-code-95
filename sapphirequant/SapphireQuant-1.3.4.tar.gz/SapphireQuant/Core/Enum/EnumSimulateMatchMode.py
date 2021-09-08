from enum import Enum, unique


@unique
class EnumSimulateMatchMode(Enum):
    last_price = 0
    bid_ask = 1
    open_price = 2
    mq_last_price = 3
    harsh_last_price = 4
    order_price = 5
