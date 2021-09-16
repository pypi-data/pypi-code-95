from enum import Enum, auto


class StreamCxnType(Enum):
    PRICING = auto()
    TRADING = auto()
    QUANTITATIVE = auto()
