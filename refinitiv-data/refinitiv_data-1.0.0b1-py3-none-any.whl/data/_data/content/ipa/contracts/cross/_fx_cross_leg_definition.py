# coding: utf8

__all__ = ["LegDefinition"]

from typing import Optional

from ..instrument._instrument_definition import ObjectDefinition
from ._enums import (
    FxLegType,
    BuySell,
)


class LegDefinition(ObjectDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    start_date : str, optional

    end_date : str, optional
        The maturity date of the contract that is the date the amounts are exchanged.
        Either the end_date or the tenor must be provided.
    tenor : str, optional
        The tenor representing the maturity date of the contract (e.g. '1Y' or '6M' ).
        Either the end_date or the tenor must be provided.
    leg_tag : str, optional
        A user defined string to identify the leg. Optional.
    deal_ccy_buy_sell : BuySell, optional
        The direction of the trade in terms of the deal currency : 'Buy' or 'Sell'.
        Optional. Defaults to 'Buy'
    fx_leg_type : FxLegType, optional
        The enumeration that specifies the type of the leg : 'Spot', 'FxForward',
        'FxNonDeliverableForward', 'SwapNear' or 'SwapFar'. Mandatory for MultiLeg,
        FwdFwdSwap, or Swap contracts. Optional for Spot and Forwards contracts.
    contra_amount : float, optional
        The unsigned amount exchanged to buy or sell the traded amount. Optional. By
        default, it is calculated from the traded rate and the deal_amount. If no traded
        rate is provided the market rate will be used.
    contra_ccy : str, optional
        The currency that is exchanged. Optional. By default, the second currency in the
        FxCrossCode.
    deal_amount : float, optional
        The unsigned amount of traded currency actually bought or sold. Optional.
        Defaults to 1,000,000'.
    deal_ccy : str, optional
        The ISO code of the traded currency (e.g. 'EUR' ). Optional. Defaults to the
        first currency of the FxCrossCode.
    start_tenor : str, optional
        The tenor representing the Starting of maturity period of the contract (e.g.
        '1Y' or '6M' ). Either the start_date or the start_tenor must be provided for
        TimeOptionForward.
    """

    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        leg_tag: Optional[str] = None,
        deal_ccy_buy_sell: Optional[BuySell] = None,
        fx_leg_type: Optional[FxLegType] = None,
        contra_amount: Optional[float] = None,
        contra_ccy: Optional[str] = None,
        deal_amount: Optional[float] = None,
        deal_ccy: Optional[str] = None,
        start_tenor: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.leg_tag = leg_tag
        self.deal_ccy_buy_sell = deal_ccy_buy_sell
        self.fx_leg_type = fx_leg_type
        self.contra_amount = contra_amount
        self.contra_ccy = contra_ccy
        self.deal_amount = deal_amount
        self.deal_ccy = deal_ccy
        self.start_tenor = start_tenor

    @property
    def deal_ccy_buy_sell(self):
        """
        The direction of the trade in terms of the deal currency : 'Buy' or 'Sell'.
        Optional. Defaults to 'Buy'
        :return: enum BuySell
        """
        return self._get_enum_parameter(BuySell, "dealCcyBuySell")

    @deal_ccy_buy_sell.setter
    def deal_ccy_buy_sell(self, value):
        self._set_enum_parameter(BuySell, "dealCcyBuySell", value)

    @property
    def fx_leg_type(self):
        """
        The enumeration that specifies the type of the leg : 'Spot', 'FxForward',
        'FxNonDeliverableForward', 'SwapNear' or 'SwapFar'. Mandatory for MultiLeg,
        FwdFwdSwap, or Swap contracts. Optional for Spot and Forwards contracts.
        :return: enum FxLegType
        """
        return self._get_enum_parameter(FxLegType, "fxLegType")

    @fx_leg_type.setter
    def fx_leg_type(self, value):
        self._set_enum_parameter(FxLegType, "fxLegType", value)

    @property
    def contra_amount(self):
        """
        The unsigned amount exchanged to buy or sell the traded amount. Optional. By
        default, it is calculated from the traded rate and the deal_amount. If no traded
        rate is provided the market rate will be used.
        :return: float
        """
        return self._get_parameter("contraAmount")

    @contra_amount.setter
    def contra_amount(self, value):
        self._set_parameter("contraAmount", value)

    @property
    def contra_ccy(self):
        """
        The currency that is exchanged. Optional. By default, the second currency in the
        FxCrossCode.
        :return: str
        """
        return self._get_parameter("contraCcy")

    @contra_ccy.setter
    def contra_ccy(self, value):
        self._set_parameter("contraCcy", value)

    @property
    def deal_amount(self):
        """
        The unsigned amount of traded currency actually bought or sold. Optional.
        Defaults to 1,000,000'.
        :return: float
        """
        return self._get_parameter("dealAmount")

    @deal_amount.setter
    def deal_amount(self, value):
        self._set_parameter("dealAmount", value)

    @property
    def deal_ccy(self):
        """
        The ISO code of the traded currency (e.g. 'EUR' ). Optional. Defaults to the
        first currency of the FxCrossCode.
        :return: str
        """
        return self._get_parameter("dealCcy")

    @deal_ccy.setter
    def deal_ccy(self, value):
        self._set_parameter("dealCcy", value)

    @property
    def end_date(self):
        """
        The maturity date of the contract that is the date the amounts are exchanged.
        Either the end_date or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def leg_tag(self):
        """
        A user defined string to identify the leg. Optional.
        :return: str
        """
        return self._get_parameter("legTag")

    @leg_tag.setter
    def leg_tag(self, value):
        self._set_parameter("legTag", value)

    @property
    def start_date(self):
        """
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def start_tenor(self):
        """
        The tenor representing the Starting of maturity period of the contract (e.g.
        '1Y' or '6M' ). Either the start_date or the Starttenor must be provided for
        TimeOptionForward.
        :return: str
        """
        return self._get_parameter("startTenor")

    @start_tenor.setter
    def start_tenor(self, value):
        self._set_parameter("startTenor", value)

    @property
    def tenor(self):
        """
        The tenor representing the maturity date of the contract (e.g. '1Y' or '6M' ).
        Either the end_date or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)
