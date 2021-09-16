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
    market_data_date : str, optional
        The market data date for pricing.
        By default, the market_data_date date is the valuation_date or Today.
    market_value_in_deal_ccy : float, optional
        market_value_in_deal_ccy to override and that will be used as pricing analysis
        input to compute VolatilityPercent. No override is applied by default.
        Note that Premium takes priority over Volatility input.
    nb_iterations : int, optional
        Used for Bermudans and HW1F tree.
    valuation_date : str, optional
        The valuation date for pricing. If not set the valuation date is equal to
        market_data_date or Today. For assets that contains a settlementConvention,
        the default valuation date  is equal to the settlementdate of the Asset that is
        usually the TradeDate+SettlementConvention.

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> rdf.swaption.PricingParameters(valuation_date="2020-04-24", nb_iterations=80)
    """

    def __init__(
        self,
        market_data_date: Optional[str] = None,
        market_value_in_deal_ccy: Optional[float] = None,
        nb_iterations: Optional[int] = None,
        valuation_date: Optional[str] = None,
    ):
        super().__init__()
        self.market_data_date = market_data_date
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.nb_iterations = nb_iterations
        self.valuation_date = valuation_date

    @property
    def market_data_date(self):
        """
        The market data date for pricing.
        By default, the marketDataDate date is the ValuationDate or Today.
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def market_value_in_deal_ccy(self):
        """
        MarketValueInDealCcy to override and that will be used as pricing analysis input to compute VolatilityPercent.
        No override is applied by default. Note that Premium takes priority over Volatility input.
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def nb_iterations(self):
        """
        Used for Bermudans and HW1F tree.
        :return: int
        """
        return self._get_parameter("nbIterations")

    @nb_iterations.setter
    def nb_iterations(self, value):
        self._set_parameter("nbIterations", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        If not set the valuation date is equal to MarketDataDate or Today.
        For assets that contains a settlementConvention, the default valuation date  is equal to
        the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
