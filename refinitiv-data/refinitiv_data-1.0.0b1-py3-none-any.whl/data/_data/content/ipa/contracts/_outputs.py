from enum import Enum, unique


@unique
class Outputs(Enum):
    HEADERS = "Headers"
    DATATYPE = "DataType"
    DATA = "Data"
    STATUSES = "Statuses"
    MARKET_DATA = "MarketData"
