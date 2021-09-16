# coding: utf8
# contract_gen 2020-05-18 08:30:59.207816

__all__ = ["StubRule"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class StubRule(Enum):
    """
    The rule that defines whether coupon roll dates are aligned on the  maturity or
       the issue date.

    The possible values are:
       - ShortFirstProRata (to create a short period between the start date and the
         first coupon date, and pay a smaller amount of interest for the short
         period.All coupon dates are calculated backward from the maturity date),
       - ShortFirstFull (to create a short period between the start date and the first
         coupon date, and pay a regular coupon on the first coupon date. All coupon
         dates are calculated backward from the maturity date),
       - LongFirstFull (to create a long period between the start date and the second
         coupon date, and pay a regular coupon on the second coupon date. All coupon
         dates are calculated backward from the maturity date),
       - ShortLastProRata (to create a short period between the last payment date and
         maturity, and pay a smaller amount of interest for the short period. All
         coupon dates are calculated forward from the start date). This property may
         also be used in conjunction with first_regular_payment_date and
         last_regular_payment_date; in that case the following values can be defined,
       - Issue (all dates are aligned on the issue date),
       - Maturity (all dates are aligned on the maturity date).
    """

    ISSUE = "Issue"
    LONG_FIRST_FULL = "LongFirstFull"
    MATURITY = "Maturity"
    SHORT_FIRST_FULL = "ShortFirstFull"
    SHORT_FIRST_PRO_RATA = "ShortFirstProRata"
    SHORT_LAST_PRO_RATA = "ShortLastProRata"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(StubRule, _STUB_RULE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_STUB_RULE_VALUES_IN_LOWER_BY_STUB_RULE, some)


_STUB_RULE_VALUES = tuple(t.value for t in StubRule)
_STUB_RULE_VALUES_IN_LOWER_BY_STUB_RULE = {
    name.lower(): item for name, item in StubRule.__members__.items()
}
