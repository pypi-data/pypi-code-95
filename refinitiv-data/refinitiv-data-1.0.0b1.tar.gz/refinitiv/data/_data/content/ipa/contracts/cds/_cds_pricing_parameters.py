# coding: utf8

__all__ = ["PricingParameters"]

from typing import Optional

from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters


class PricingParameters(InstrumentPricingParameters):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    cash_amount_in_deal_ccy : float, optional
        cash_amount_in_deal_ccy to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    clean_price_percent : float, optional
        clean_price_percent to override and that will be used as pricing analysis input
        to compute the cds other outputs. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
    conventional_spread_bp : float, optional
        conventional_spread_bp to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    market_data_date : str, optional
        The market data date for pricing. Optional. By default, the market_data_date
        date is the valuation_date or Today
    upfront_amount_in_deal_ccy : float, optional
        upfront_amount_in_deal_ccy to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
    upfront_percent : float, optional
        upfront_percent to override and that will be used as pricing analysis input to
        compute the cds other outputs. Optional. No override is applied by default. Note
        that only one pricing analysis input should be defined.
    valuation_date : str, optional
        The valuation date for pricing.  Optional. If not set the valuation date is
        equal to market_data_date or Today. For assets that contains a
        settlementConvention, the default valuation date  is equal to the settlementdate
        of the Asset that is usually the TradeDate+SettlementConvention.
    """

    def __init__(
        self,
        *,
        cash_amount_in_deal_ccy: Optional[float] = None,
        clean_price_percent: Optional[float] = None,
        conventional_spread_bp: Optional[float] = None,
        market_data_date: Optional[str] = None,
        upfront_amount_in_deal_ccy: Optional[float] = None,
        upfront_percent: Optional[float] = None,
        valuation_date: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.cash_amount_in_deal_ccy = cash_amount_in_deal_ccy
        self.clean_price_percent = clean_price_percent
        self.conventional_spread_bp = conventional_spread_bp
        self.market_data_date = market_data_date
        self.upfront_amount_in_deal_ccy = upfront_amount_in_deal_ccy
        self.upfront_percent = upfront_percent
        self.valuation_date = valuation_date

    @property
    def cash_amount_in_deal_ccy(self):
        """
        cash_amount_in_deal_ccy to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cashAmountInDealCcy")

    @cash_amount_in_deal_ccy.setter
    def cash_amount_in_deal_ccy(self, value):
        self._set_parameter("cashAmountInDealCcy", value)

    @property
    def clean_price_percent(self):
        """
        clean_price_percent to override and that will be used as pricing analysis input
        to compute the cds other outputs. Optional. No override is applied by default.
        Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cleanPricePercent")

    @clean_price_percent.setter
    def clean_price_percent(self, value):
        self._set_parameter("cleanPricePercent", value)

    @property
    def conventional_spread_bp(self):
        """
        conventional_spread_bp to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("conventionalSpreadBp")

    @conventional_spread_bp.setter
    def conventional_spread_bp(self, value):
        self._set_parameter("conventionalSpreadBp", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing. Optional. By default, the market_data_date
        date is the valuation_date or Today
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def upfront_amount_in_deal_ccy(self):
        """
        upfront_amount_in_deal_ccy to override and that will be used as pricing analysis
        input to compute the cds other outputs. Optional. No override is applied by
        default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("upfrontAmountInDealCcy")

    @upfront_amount_in_deal_ccy.setter
    def upfront_amount_in_deal_ccy(self, value):
        self._set_parameter("upfrontAmountInDealCcy", value)

    @property
    def upfront_percent(self):
        """
        upfront_percent to override and that will be used as pricing analysis input to
        compute the cds other outputs. Optional. No override is applied by default. Note
        that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("upfrontPercent")

    @upfront_percent.setter
    def upfront_percent(self, value):
        self._set_parameter("upfrontPercent", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.  Optional. If not set the valuation date is
        equal to market_data_date or Today. For assets that contains a
        settlementConvention, the default valuation date  is equal to the settlementdate
        of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
