# coding: utf8
# contract_gen 2020-05-18 08:30:59.210816

__all__ = ["RedemptionDateType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class RedemptionDateType(Enum):
    """
    Redemption type of the bond.

    It is used to compute the default redemption date:
        - RedemptionAtMaturityDate : yield and price are computed at maturity date.
        - RedemptionAtCallDate : yield and price are computed at call date (next call
          date by default).
        - RedemptionAtPutDate : yield and price are computed at put date (next put date
          by default)..
        - RedemptionAtWorstDate : yield and price are computed at the lowest yield date.
        - RedemptionAtSinkDate : yield and price are computed at sinking fund date.
        - RedemptionAtParDate : yield and price are computed at next par.
        - RedemptionAtPremiumDate : yield and price are computed at next premium.
        - RedemptionAtMakeWholeCallDate : yield and price are computed at Make Whole
          Call date.
        - RedemptionAtAverageLife : yield and price are computed at average life (case
          of sinkable bonds)
        - RedemptionAtNextDate : yield and price are computed at next redemption date
          available.
    """

    REDEMPTION_AT_AVERAGE_LIFE = "RedemptionAtAverageLife"
    REDEMPTION_AT_BEST_DATE = "RedemptionAtBestDate"
    REDEMPTION_AT_CALL_DATE = "RedemptionAtCallDate"
    REDEMPTION_AT_CUSTOM_DATE = "RedemptionAtCustomDate"
    REDEMPTION_AT_MAKE_WHOLE_CALL_DATE = "RedemptionAtMakeWholeCallDate"
    REDEMPTION_AT_MATURITY_DATE = "RedemptionAtMaturityDate"
    REDEMPTION_AT_NEXT_DATE = "RedemptionAtNextDate"
    REDEMPTION_AT_PAR_DATE = "RedemptionAtParDate"
    REDEMPTION_AT_PARTIAL_CALL_DATE = "RedemptionAtPartialCallDate"
    REDEMPTION_AT_PARTIAL_PUT_DATE = "RedemptionAtPartialPutDate"
    REDEMPTION_AT_PERPETUITY = "RedemptionAtPerpetuity"
    REDEMPTION_AT_PREMIUM_DATE = "RedemptionAtPremiumDate"
    REDEMPTION_AT_PUT_DATE = "RedemptionAtPutDate"
    REDEMPTION_AT_SINK_DATE = "RedemptionAtSinkDate"
    REDEMPTION_AT_WORST_DATE = "RedemptionAtWorstDate"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(RedemptionDateType, _REDEMPTION_DATE_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _REDEMPTION_DATE_TYPE_VALUES_IN_LOWER_BY_REDEMPTION_DATE_TYPE, some
        )


_REDEMPTION_DATE_TYPE_VALUES = tuple(t.value for t in RedemptionDateType)
_REDEMPTION_DATE_TYPE_VALUES_IN_LOWER_BY_REDEMPTION_DATE_TYPE = {
    name.lower(): item for name, item in RedemptionDateType.__members__.items()
}
