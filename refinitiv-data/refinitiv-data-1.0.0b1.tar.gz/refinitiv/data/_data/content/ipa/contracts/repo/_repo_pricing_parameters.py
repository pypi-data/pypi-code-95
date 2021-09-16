# coding: utf8


__all__ = ["PricingParameters"]

from typing import Optional

from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters
from ._enums import RepoCurveType


class PricingParameters(InstrumentPricingParameters):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    repo_curve_type : RepoCurveType, optional
        Curve used to compute the repo rate.
        If no curve can be found, the rate is computed using a deposit curve.
    market_data_date : str, optional
        The market data date for pricing.
        By default, the market_data_date date is the valuation_date or Today
    valuation_date : str, optional
        The valuation date for pricing. If not set the valuation date is equal to
        market_data_date or Today. For assets that contains a settlementConvention,
        the default valuation date  is equal to the settlementdate of the Asset that
        is usually the TradeDate+SettlementConvention.

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> rdf.repo.PricingParameters(market_data_date="2019-11-25")
    """

    def __init__(
        self,
        repo_curve_type: Optional[RepoCurveType] = None,
        market_data_date: Optional[str] = None,
        valuation_date: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.repo_curve_type = repo_curve_type
        self.market_data_date = market_data_date
        self.valuation_date = valuation_date

    @property
    def repo_curve_type(self):
        """
        Curve used to compute the repo rate. it can be computed using following methods:
            - RepoCurve : rate is computed by interpolating a repo curve.
            - DepositCurve : rate is computed by interpolating a deposit curve.
            - LiborFixing : rate is computed by interpolating libor rates.
        If no curve can be found, the rate is computed using a deposit curve.
        :return: enum RepoCurveType
        """
        return self._get_enum_parameter(RepoCurveType, "repoCurveType")

    @repo_curve_type.setter
    def repo_curve_type(self, value):
        self._set_enum_parameter(RepoCurveType, "repoCurveType", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing.
        By default, the market_data_date date is the valuation_date or Today
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing. If not set the valuation date is equal to
        market_data_date or Today. For assets that contains a settlementConvention, the
        default valuation date  is equal to the settlementdate of the Asset that is
        usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
