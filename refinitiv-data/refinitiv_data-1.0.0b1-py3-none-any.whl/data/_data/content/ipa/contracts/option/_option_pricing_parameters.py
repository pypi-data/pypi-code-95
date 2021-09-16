# coding: utf8

__all__ = ["PricingParameters"]

from typing import Optional

from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters
from ._enums import (
    FxSwapCalculationMethod,
    OptionVolatilityType,
    PriceSide,
    PricingModelType,
    TimeStamp,
    VolatilityModel,
)
from ._models import (
    BidAskMid,
    InterpolationWeight,
    PayoutScaling,
)


class PricingParameters(InstrumentPricingParameters):
    """
    Parameters
    ----------
    atm_volatility_object : BidAskMid, optional
        At the money volatility at Expiry
    butterfly10_d_object : BidAskMid, optional
        BF 10 Days at Expiry
    butterfly25_d_object : BidAskMid, optional
        BF 25 Days at Expiry
    domestic_deposit_rate_percent_object : BidAskMid, optional
        Domestic Deposit Rate at Expiry
    foreign_deposit_rate_percent_object : BidAskMid, optional
        Foreign Deposit Rate at Expiry
    forward_points_object : BidAskMid, optional
        Forward Points at Expiry
    fx_spot_object : BidAskMid, optional
        Spot Price
    fx_swap_calculation_method : FxSwapCalculationMethod, optional
        The method we chose to price outrights using or not implied deposits. Possible
        values are:   FxSwap (compute outrights using swap points),
        FxSwapImpliedFromDeposit (compute swap points using deposits of currency1 and
        currency2),   DepositCcy1ImpliedFromFxSwap (compute currency1 deposits using
        swap points),   DepositCcy2ImpliedFromFxSwap (compute currency2 deposits using
        swap points).   Optional. Defaults to 'DepositCcy2ImpliedFromFxSwap'.
    implied_volatility_object : BidAskMid, optional
        Implied volatility at Expiry
    interpolation_weight : InterpolationWeight, optional
        Vol Term Structure Interpolation
    option_price_side : PriceSide, optional
        Quoted option's price side to use for pricing Analysis: Bid(Bid value), Ask(Ask
        value), Mid(Mid value), Last(Last value). Optional. By default the "Mid" price
        of the option is used.
    option_time_stamp : TimeStamp, optional
        Define how the timestamp of the option is selected:
        - Open: the opening value of the valuation_date or if not available the close of
          the previous day is used.
        - Default: the latest snapshot is used when valuation_date is today, the close
          price when valuation_date is in the past.
    payout_custom_dates : string, optional
        Define the custom dates for the Payout/Volatility chart
    payout_scaling_interval : PayoutScaling, optional
        Define the range for the Payout/Volatility chart
    price_side : PriceSide, optional
        The enumerate that specifies whether bid, ask or mid is used to price the Fx
        option. Possible values:
        - Bid
        - Ask
        - Mid
        - Last
    pricing_model_type : PricingModelType, optional
        The enumeration that specifies the model type of pricing. Possible values:
        - BlackScholes
        - Whaley
        - Binomial
        - Trinomial
        - VannaVolga
    risk_reversal10_d_object : BidAskMid, optional
        RR 10 Days at Expiry
    risk_reversal25_d_object : BidAskMid, optional
        RR 25 Days at Expiry
    underlying_price_side : PriceSide, optional
        Quoted underlying's price side to use for pricing Analysis: Bid(Bid value),
        Ask(Ask value), Mid(Mid value), Last(Last value). Optional. By default the
        "Last" price of the underlying is used.
    underlying_time_stamp : TimeStamp, optional
        Define how the timestamp of the underlying is selected:
        - Open: the opening value of the valuation_date or if not available the close of
          the previous day is used.
        - Default: the latest snapshot is used when valuation_date is today, the close
          price when valuation_date is in the past.
    volatility_model : VolatilityModel, optional
        The quantitative model used to generate the volatility surface. This may depend
        on the asset class. For Fx Volatility Surface, we currently support the SVI
        model.
    volatility_type : OptionVolatilityType, optional
        The type of volatility for the option's pricing. It can be Implied or
        SVISurface. Optional. Default to Implied. Note that if Volatility is defined,
        volatility_type is not taken into account.
    compute_payout_chart : bool, optional

    compute_volatility_payout : bool, optional

    cutoff_time : str, optional
        The cutoff time
    cutoff_time_zone : str, optional
        The cutoff time zone
    market_data_date : str, optional
        The market data date for pricing. Optional. By default, the market_data_date
        date is the valuation_date or Today
    market_value_in_deal_ccy : float, optional
        market_value_in_deal_ccy to override and that will be used as pricing analysis
        input to compute volatility_percent. Optional. No override is applied by
        default. Note that Premium takes priority over Volatility input.
    report_ccy_rate : float, optional
        Define the spot rate to use with the currency report
    risk_free_rate_percent : float, optional
        risk_free_rate_percent to override and that will be used as pricing analysis
        input to compute the option other outputs. Optional. No override is applied by
        default.
    underlying_price : float, optional
        underlying_price to override and that will be used as pricing analysis input to
        compute the option other outputs. Optional. No override is applied by default.
    valuation_date : str, optional
        The valuation date for pricing.  Optional. If not set the valuation date is
        equal to market_data_date or Today. For assets that contains a
        settlementConvention, the default valuation date  is equal to the settlementdate
        of the Asset that is usually the TradeDate+SettlementConvention.
    volatility_percent : float, optional
        volatility_percent to override and that will be used as pricing analysis input
        to compute market_value_in_deal_ccy. Optional. No override is applied by
        default. Note that if Premium is defined, volatility_percent is not taken into
        account.
    """

    def __init__(
        self,
        atm_volatility_object: Optional[BidAskMid] = None,
        butterfly10_d_object: Optional[BidAskMid] = None,
        butterfly25_d_object: Optional[BidAskMid] = None,
        domestic_deposit_rate_percent_object: Optional[BidAskMid] = None,
        foreign_deposit_rate_percent_object: Optional[BidAskMid] = None,
        forward_points_object: Optional[BidAskMid] = None,
        fx_spot_object: Optional[BidAskMid] = None,
        fx_swap_calculation_method: Optional[FxSwapCalculationMethod] = None,
        implied_volatility_object: Optional[BidAskMid] = None,
        interpolation_weight: Optional[InterpolationWeight] = None,
        option_price_side: Optional[PriceSide] = None,
        option_time_stamp: Optional[TimeStamp] = None,
        payout_custom_dates: Optional[str] = None,
        payout_scaling_interval: Optional[PayoutScaling] = None,
        price_side: Optional[PriceSide] = None,
        pricing_model_type: Optional[PricingModelType] = None,
        risk_reversal10_d_object: Optional[BidAskMid] = None,
        risk_reversal25_d_object: Optional[BidAskMid] = None,
        underlying_price_side: Optional[PriceSide] = None,
        underlying_time_stamp: Optional[TimeStamp] = None,
        volatility_model: Optional[VolatilityModel] = None,
        volatility_type: Optional[OptionVolatilityType] = None,
        compute_payout_chart: Optional[bool] = None,
        compute_volatility_payout: Optional[bool] = None,
        cutoff_time: Optional[str] = None,
        cutoff_time_zone: Optional[str] = None,
        market_data_date: Optional[str] = None,
        market_value_in_deal_ccy: Optional[float] = None,
        report_ccy_rate: Optional[float] = None,
        risk_free_rate_percent: Optional[float] = None,
        underlying_price: Optional[float] = None,
        valuation_date: Optional[str] = None,
        volatility_percent: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.atm_volatility_object = atm_volatility_object
        self.butterfly10_d_object = butterfly10_d_object
        self.butterfly25_d_object = butterfly25_d_object
        self.domestic_deposit_rate_percent_object = domestic_deposit_rate_percent_object
        self.foreign_deposit_rate_percent_object = foreign_deposit_rate_percent_object
        self.forward_points_object = forward_points_object
        self.fx_spot_object = fx_spot_object
        self.fx_swap_calculation_method = fx_swap_calculation_method
        self.implied_volatility_object = implied_volatility_object
        self.interpolation_weight = interpolation_weight
        self.option_price_side = option_price_side
        self.option_time_stamp = option_time_stamp
        self.payout_custom_dates = payout_custom_dates
        self.payout_scaling_interval = payout_scaling_interval
        self.price_side = price_side
        self.pricing_model_type = pricing_model_type
        self.risk_reversal10_d_object = risk_reversal10_d_object
        self.risk_reversal25_d_object = risk_reversal25_d_object
        self.underlying_price_side = underlying_price_side
        self.underlying_time_stamp = underlying_time_stamp
        self.volatility_model = volatility_model
        self.volatility_type = volatility_type
        self.compute_payout_chart = compute_payout_chart
        self.compute_volatility_payout = compute_volatility_payout
        self.cutoff_time = cutoff_time
        self.cutoff_time_zone = cutoff_time_zone
        self.market_data_date = market_data_date
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.report_ccy_rate = report_ccy_rate
        self.risk_free_rate_percent = risk_free_rate_percent
        self.underlying_price = underlying_price
        self.valuation_date = valuation_date
        self.volatility_percent = volatility_percent

    @property
    def atm_volatility_object(self):
        """
        At the money volatility at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "atmVolatilityObject")

    @atm_volatility_object.setter
    def atm_volatility_object(self, value):
        self._set_object_parameter(BidAskMid, "atmVolatilityObject", value)

    @property
    def butterfly10_d_object(self):
        """
        BF 10 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "butterfly10DObject")

    @butterfly10_d_object.setter
    def butterfly10_d_object(self, value):
        self._set_object_parameter(BidAskMid, "butterfly10DObject", value)

    @property
    def butterfly25_d_object(self):
        """
        BF 25 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "butterfly25DObject")

    @butterfly25_d_object.setter
    def butterfly25_d_object(self, value):
        self._set_object_parameter(BidAskMid, "butterfly25DObject", value)

    @property
    def domestic_deposit_rate_percent_object(self):
        """
        Domestic Deposit Rate at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "domesticDepositRatePercentObject")

    @domestic_deposit_rate_percent_object.setter
    def domestic_deposit_rate_percent_object(self, value):
        self._set_object_parameter(BidAskMid, "domesticDepositRatePercentObject", value)

    @property
    def foreign_deposit_rate_percent_object(self):
        """
        Foreign Deposit Rate at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "foreignDepositRatePercentObject")

    @foreign_deposit_rate_percent_object.setter
    def foreign_deposit_rate_percent_object(self, value):
        self._set_object_parameter(BidAskMid, "foreignDepositRatePercentObject", value)

    @property
    def forward_points_object(self):
        """
        Forward Points at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "forwardPointsObject")

    @forward_points_object.setter
    def forward_points_object(self, value):
        self._set_object_parameter(BidAskMid, "forwardPointsObject", value)

    @property
    def fx_spot_object(self):
        """
        Spot Price
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "fxSpotObject")

    @fx_spot_object.setter
    def fx_spot_object(self, value):
        self._set_object_parameter(BidAskMid, "fxSpotObject", value)

    @property
    def fx_swap_calculation_method(self):
        """
        The method we chose to price outrights using or not implied deposits. Possible
        values are:   FxSwap (compute outrights using swap points),
        FxSwapImpliedFromDeposit (compute swap points using deposits of currency1 and
        currency2),   DepositCcy1ImpliedFromFxSwap (compute currency1 deposits using
        swap points),   DepositCcy2ImpliedFromFxSwap (compute currency2 deposits using
        swap points).   Optional. Defaults to 'DepositCcy2ImpliedFromFxSwap'.
        :return: enum FxSwapCalculationMethod
        """
        return self._get_enum_parameter(
            FxSwapCalculationMethod, "fxSwapCalculationMethod"
        )

    @fx_swap_calculation_method.setter
    def fx_swap_calculation_method(self, value):
        self._set_enum_parameter(
            FxSwapCalculationMethod, "fxSwapCalculationMethod", value
        )

    @property
    def implied_volatility_object(self):
        """
        Implied volatility at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "impliedVolatilityObject")

    @implied_volatility_object.setter
    def implied_volatility_object(self, value):
        self._set_object_parameter(BidAskMid, "impliedVolatilityObject", value)

    @property
    def interpolation_weight(self):
        """
        Vol Term Structure Interpolation
        :return: object InterpolationWeight
        """
        return self._get_object_parameter(InterpolationWeight, "interpolationWeight")

    @interpolation_weight.setter
    def interpolation_weight(self, value):
        self._set_object_parameter(InterpolationWeight, "interpolationWeight", value)

    @property
    def option_price_side(self):
        """
        Quoted option's price side to use for pricing Analysis: Bid(Bid value), Ask(Ask
        value), Mid(Mid value), Last(Last value). Optional. By default the "Mid" price
        of the option is used.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "optionPriceSide")

    @option_price_side.setter
    def option_price_side(self, value):
        self._set_enum_parameter(PriceSide, "optionPriceSide", value)

    @property
    def option_time_stamp(self):
        """
        Define how the timestamp of the option is selected:
        - Open: the opening value of the valuation_date or if not available the close of
          the previous day is used.
        - Default: the latest snapshot is used when valuation_date is today, the close
          price when valuation_date is in the past.
        :return: enum TimeStamp
        """
        return self._get_enum_parameter(TimeStamp, "optionTimeStamp")

    @option_time_stamp.setter
    def option_time_stamp(self, value):
        self._set_enum_parameter(TimeStamp, "optionTimeStamp", value)

    @property
    def payout_custom_dates(self):
        """
        Define the custom dates for the Payout/Volatility chart
        :return: list string
        """
        return self._get_list_parameter(str, "payoutCustomDates")

    @payout_custom_dates.setter
    def payout_custom_dates(self, value):
        self._set_list_parameter(str, "payoutCustomDates", value)

    @property
    def payout_scaling_interval(self):
        """
        Define the range for the Payout/Volatility chart
        :return: object PayoutScaling
        """
        return self._get_object_parameter(PayoutScaling, "payoutScalingInterval")

    @payout_scaling_interval.setter
    def payout_scaling_interval(self, value):
        self._set_object_parameter(PayoutScaling, "payoutScalingInterval", value)

    @property
    def price_side(self):
        """
        The enumerate that specifies whether bid, ask or mid is used to price the Fx
        option. Possible values:
        - Bid
        - Ask
        - Mid
        - Last
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def pricing_model_type(self):
        """
        The enumeration that specifies the model type of pricing. Possible values:
        - BlackScholes
        - Whaley
        - Binomial
        - Trinomial
        - VannaVolga
        :return: enum PricingModelType
        """
        return self._get_enum_parameter(PricingModelType, "pricingModelType")

    @pricing_model_type.setter
    def pricing_model_type(self, value):
        self._set_enum_parameter(PricingModelType, "pricingModelType", value)

    @property
    def risk_reversal10_d_object(self):
        """
        RR 10 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "riskReversal10DObject")

    @risk_reversal10_d_object.setter
    def risk_reversal10_d_object(self, value):
        self._set_object_parameter(BidAskMid, "riskReversal10DObject", value)

    @property
    def risk_reversal25_d_object(self):
        """
        RR 25 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "riskReversal25DObject")

    @risk_reversal25_d_object.setter
    def risk_reversal25_d_object(self, value):
        self._set_object_parameter(BidAskMid, "riskReversal25DObject", value)

    @property
    def underlying_price_side(self):
        """
        Quoted underlying's price side to use for pricing Analysis: Bid(Bid value),
        Ask(Ask value), Mid(Mid value), Last(Last value). Optional. By default the
        "Last" price of the underlying is used.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "underlyingPriceSide")

    @underlying_price_side.setter
    def underlying_price_side(self, value):
        self._set_enum_parameter(PriceSide, "underlyingPriceSide", value)

    @property
    def underlying_time_stamp(self):
        """
        Define how the timestamp of the underlying is selected:
        - Open: the opening value of the valuation_date or if not available the close of
          the previous day is used.
        - Default: the latest snapshot is used when valuation_date is today, the close
          price when valuation_date is in the past.
        :return: enum TimeStamp
        """
        return self._get_enum_parameter(TimeStamp, "underlyingTimeStamp")

    @underlying_time_stamp.setter
    def underlying_time_stamp(self, value):
        self._set_enum_parameter(TimeStamp, "underlyingTimeStamp", value)

    @property
    def volatility_model(self):
        """
        The quantitative model used to generate the volatility surface. This may depend
        on the asset class. For Fx Volatility Surface, we currently support the SVI
        model.
        :return: enum VolatilityModel
        """
        return self._get_enum_parameter(VolatilityModel, "volatilityModel")

    @volatility_model.setter
    def volatility_model(self, value):
        self._set_enum_parameter(VolatilityModel, "volatilityModel", value)

    @property
    def volatility_type(self):
        """
        The type of volatility for the option's pricing. It can be Implied or
        SVISurface. Optional. Default to Implied. Note that if Volatility is defined,
        volatility_type is not taken into account.
        :return: enum OptionVolatilityType
        """
        return self._get_enum_parameter(OptionVolatilityType, "volatilityType")

    @volatility_type.setter
    def volatility_type(self, value):
        self._set_enum_parameter(OptionVolatilityType, "volatilityType", value)

    @property
    def compute_payout_chart(self):
        """
        :return: bool
        """
        return self._get_parameter("computePayoutChart")

    @compute_payout_chart.setter
    def compute_payout_chart(self, value):
        self._set_parameter("computePayoutChart", value)

    @property
    def compute_volatility_payout(self):
        """
        :return: bool
        """
        return self._get_parameter("computeVolatilityPayout")

    @compute_volatility_payout.setter
    def compute_volatility_payout(self, value):
        self._set_parameter("computeVolatilityPayout", value)

    @property
    def cutoff_time(self):
        """
        The cutoff time
        :return: str
        """
        return self._get_parameter("cutoffTime")

    @cutoff_time.setter
    def cutoff_time(self, value):
        self._set_parameter("cutoffTime", value)

    @property
    def cutoff_time_zone(self):
        """
        The cutoff time zone
        :return: str
        """
        return self._get_parameter("cutoffTimeZone")

    @cutoff_time_zone.setter
    def cutoff_time_zone(self, value):
        self._set_parameter("cutoffTimeZone", value)

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
    def market_value_in_deal_ccy(self):
        """
        market_value_in_deal_ccy to override and that will be used as pricing analysis
        input to compute volatility_percent. Optional. No override is applied by
        default. Note that Premium takes priority over Volatility input.
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def report_ccy_rate(self):
        """
        Define the spot rate to use with the currency report
        :return: float
        """
        return self._get_parameter("reportCcyRate")

    @report_ccy_rate.setter
    def report_ccy_rate(self, value):
        self._set_parameter("reportCcyRate", value)

    @property
    def risk_free_rate_percent(self):
        """
        risk_free_rate_percent to override and that will be used as pricing analysis
        input to compute the option other outputs. Optional. No override is applied by
        default.
        :return: float
        """
        return self._get_parameter("riskFreeRatePercent")

    @risk_free_rate_percent.setter
    def risk_free_rate_percent(self, value):
        self._set_parameter("riskFreeRatePercent", value)

    @property
    def underlying_price(self):
        """
        underlying_price to override and that will be used as pricing analysis input to
        compute the option other outputs. Optional. No override is applied by default.
        :return: float
        """
        return self._get_parameter("underlyingPrice")

    @underlying_price.setter
    def underlying_price(self, value):
        self._set_parameter("underlyingPrice", value)

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

    @property
    def volatility_percent(self):
        """
        volatility_percent to override and that will be used as pricing analysis input
        to compute market_value_in_deal_ccy. Optional. No override is applied by
        default. Note that if Premium is defined, volatility_percent is not taken into
        account.
        :return: float
        """
        return self._get_parameter("volatilityPercent")

    @volatility_percent.setter
    def volatility_percent(self, value):
        self._set_parameter("volatilityPercent", value)
