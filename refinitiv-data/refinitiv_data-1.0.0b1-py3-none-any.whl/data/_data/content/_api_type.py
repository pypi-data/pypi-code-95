from enum import Enum, auto


class APIType(Enum):
    FINANCIAL_CONTRACTS = auto()
    CURVES_AND_SURFACES = auto()
    HISTORICAL_PRICING = auto()
    ESG = auto()
    PRICING = auto()
