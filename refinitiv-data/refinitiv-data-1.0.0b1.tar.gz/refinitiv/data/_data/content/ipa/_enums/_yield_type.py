# coding: utf8
# contract_gen 2020-05-18 08:30:59.213816

__all__ = ["YieldType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class YieldType(Enum):
    """
    YieldType that specifies the rate structure:
    - Native : no specific yield type is defined.
    - UsGovt_Actual_Actual_6M : US Govt Act/Act 6M YTA.
    - Isma_30_360_6M : ISMA 30/360 6M YTA.
    - Euroland_Actual_Actual_6M : Euroland Equivalent Act/Act 6M YTA.
    - Money_Market_Actual_360_6M : Money Market Act/360 6M YTA.
    - Money_Market_Actual_365_6M : Money Market Act/365 6M YTA.
    - Money_Market_Actual_Actual_6M : Money Market Act/Act 6M YTA.
    - Bond_Actual_364_6M : Bond Market Act/364 6M YTA.
    - Japanese_Simple_JAP_6M : Japanese Simple JAP 6M YTA.
    - Japanese_Compunded_30_360_6M : Japanese Compounded 30/360 6M YTA.
    - Moosmueller_30_360_6M : Moosmueller 30/360 6M YTA.
    - Braess_Frangmeyer_30_360_6M : Braess-Frangmeyer 30/360 6M YTA.
    - Weekend_30_360 : Week End 30/360 6M YTA.
    """

    ANNUAL_EQUIVALENT = "Annual_Equivalent"
    BOND_ACTUAL_364 = "Bond_Actual_364"
    BRAESS_FANGMEYER = "Braess_Fangmeyer"
    DISCOUNT_ACTUAL_360 = "Discount_Actual_360"
    DISCOUNT_ACTUAL_365 = "Discount_Actual_365"
    EUROLAND = "Euroland"
    ISMA = "Isma"
    JAPANESE_COMPOUNDED = "Japanese_Compounded"
    JAPANESE_SIMPLE = "Japanese_Simple"
    MONEY_MARKET_ACTUAL_360 = "MoneyMarket_Actual_360"
    MONEY_MARKET_ACTUAL_365 = "MoneyMarket_Actual_365"
    MONEY_MARKET_ACTUAL_ACTUAL = "MoneyMarket_Actual_Actual"
    MOOSMUELLER = "Moosmueller"
    NATIVE = "Native"
    QUARTERLY_EQUIVALENT = "Quarterly_Equivalent"
    SEMIANNUAL_EQUIVALENT = "Semiannual_Equivalent"
    TURKISH_COMPOUNDED = "TurkishCompounded"
    US_GOVT = "UsGovt"
    US_T_BILLS = "UsTBills"
    WEEKEND = "Weekend"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(YieldType, _YIELD_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_YIELD_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE, some)


_YIELD_TYPE_VALUES = tuple(t.value for t in YieldType)
_YIELD_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE = {
    name.lower(): item for name, item in YieldType.__members__.items()
}
