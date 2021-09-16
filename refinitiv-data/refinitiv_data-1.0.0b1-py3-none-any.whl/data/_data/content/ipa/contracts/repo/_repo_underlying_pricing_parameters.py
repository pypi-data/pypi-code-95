# coding: utf8

__all__ = ["UnderlyingPricingParameters"]

from . import RepoParameters
from ..bond import PricingParameters as BondPricingParameters
from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters


class UnderlyingPricingParameters(InstrumentPricingParameters):
    def __init__(
        self,
        repo_parameters=None,
        pricing_parameters_at_end=None,
        pricing_parameters_at_start=None,
        valuation_date=None,
        market_data_date=None,
    ):
        super().__init__()
        self.pricing_parameters_at_end = pricing_parameters_at_end
        self.pricing_parameters_at_start = pricing_parameters_at_start
        self.repo_parameters = repo_parameters
        self.valuation_date = valuation_date
        self.market_data_date = market_data_date

    @property
    def pricing_parameters_at_end(self):
        """
        Pricing parameters of underlying bond at Repo end date.
        :return: object BondPricingParameters
        """
        return self._get_object_parameter(
            BondPricingParameters, "pricingParametersAtEnd"
        )

    @pricing_parameters_at_end.setter
    def pricing_parameters_at_end(self, value):
        self._set_object_parameter(
            BondPricingParameters, "pricingParametersAtEnd", value
        )

    @property
    def pricing_parameters_at_start(self):
        """
        Pricing parameters of underlying bond at Repo start date.
        :return: object BondPricingParameters
        """
        return self._get_object_parameter(
            BondPricingParameters, "pricingParametersAtStart"
        )

    @pricing_parameters_at_start.setter
    def pricing_parameters_at_start(self, value):
        self._set_object_parameter(
            BondPricingParameters, "pricingParametersAtStart", value
        )

    @property
    def repo_parameters(self):
        """
        Repo parameters to be applied on underlying bond.
        :return: object RepoParameters
        """
        return self._get_object_parameter(RepoParameters, "repoParameters")

    @repo_parameters.setter
    def repo_parameters(self, value):
        self._set_object_parameter(RepoParameters, "repoParameters", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. If not set the valuation date is equal to MarketDataDate or Today. For assets that contains a settlementConvention,
        the default valuation date  is equal to the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing.
        Optional. By default, the marketDataDate date is the ValuationDate or Today
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)
