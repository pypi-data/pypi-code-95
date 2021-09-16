from enum import Enum, auto


class ContentType(Enum):
    FORWARD_CURVE = auto()
    ZC_CURVES = auto()
    ZC_CURVE_DEFINITIONS = auto()
    SURFACES = auto()
    CONTRACTS = auto()
    HISTORICAL_PRICING_EVENTS = auto()
    HISTORICAL_PRICING_INTERDAY_SUMMARIES = auto()
    HISTORICAL_PRICING_INTRADAY_SUMMARIES = auto()
    ESG_STANDARD_SCORES = auto()
    ESG_STANDARD_MEASURES = auto()
    ESG_FULL_MEASURES = auto()
    ESG_FULL_SCORES = auto()
    ESG_BASIC_OVERVIEW = auto()
    ESG_UNIVERSE = auto()
    PRICING = auto()
