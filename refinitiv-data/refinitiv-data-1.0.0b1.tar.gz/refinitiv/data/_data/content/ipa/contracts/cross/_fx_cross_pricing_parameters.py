# coding: utf8

__all__ = ["PricingParameters"]

from typing import Optional

from ._enums import (
    PriceSide,
    FxSwapCalculationMethod,
)
from ._models import FxPoint
from ..instrument._instrument_pricing_parameters import InstrumentPricingParameters


class PricingParameters(InstrumentPricingParameters):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    deposit_ccy1 : FxPoint, optional

    deposit_ccy2 : FxPoint, optional

    fx_swap_calculation_method : FxSwapCalculationMethod, optional
        The method we chose to price outrights using or not implied deposits. Possible
        values are:   FxSwap (compute outrights using swap points),
        deposit_ccy1ImpliedFromFxSwap (compute currency1 deposits using swap points),
        deposit_ccy2ImpliedFromFxSwap (compute currency2 deposits using swap points).
        Optional. Defaults to 'FxSwap'.
    fx_swaps_ccy1 : FxPoint, optional

    fx_swaps_ccy1_ccy2 : FxPoint, optional

    fx_swaps_ccy2 : FxPoint, optional

    fx_swaps_far_leg : FxPoint, optional

    fx_swaps_near_leg : FxPoint, optional

    price_side : PriceSide, optional
        The type of price returned for pricing Analysis: Bid(Bid value), Ask(Ask value),
        Mid(Mid value) Optional. Defaults to 'Mid'.
    adjust_all_swap_points_to_cross_calendars : bool, optional
        This flag define if cross-calendar holidays should be taken into account for
        fx_swaps_ccy1 and fx_swaps_ccy2. it adjusts swap points according to cross
        holidays if it's set to true, by default set to false.
    calc_end_from_fwd_start : bool, optional

    calc_end_from_pre_spot_start : bool, optional

    ignore_ref_ccy_holidays : bool, optional
        The reference currency holidays flag : When dates are computed, its possible to
        choose if holidays of the reference currency are included or not in the pricing
        Optional. Defaults to 'false'.
    market_data_date : str, optional
        The market data date for pricing. Optional. By default, the market_data_date
        date is the valuation_date or Today
    one_day_values : str, optional

    roll_over_time_policy : str, optional

    spread_margin_in_bp : float, optional
        If activated, it will calculate the indicated points in market data section
        instead of taking them directly from the curves
    valuation_date : str, optional
        The valuation date for pricing.  Optional. If not set the valuation date is
        equal to market_data_date or Today. For assets that contains a
        settlementConvention, the default valuation date  is equal to the settlementdate
        of the Asset that is usually the TradeDate+SettlementConvention.
    """

    def __init__(
        self,
        deposit_ccy1: Optional[FxPoint] = None,
        deposit_ccy2: Optional[FxPoint] = None,
        fx_swap_calculation_method: Optional[FxSwapCalculationMethod] = None,
        fx_swaps_ccy1: Optional[FxPoint] = None,
        fx_swaps_ccy1_ccy2: Optional[FxPoint] = None,
        fx_swaps_ccy2: Optional[FxPoint] = None,
        fx_swaps_far_leg: Optional[FxPoint] = None,
        fx_swaps_near_leg: Optional[FxPoint] = None,
        price_side: Optional[PriceSide] = None,
        adjust_all_swap_points_to_cross_calendars: Optional[bool] = None,
        calc_end_from_fwd_start: Optional[bool] = None,
        calc_end_from_pre_spot_start: Optional[bool] = None,
        ignore_ref_ccy_holidays: Optional[bool] = None,
        market_data_date: Optional[str] = None,
        one_day_values: Optional[str] = None,
        roll_over_time_policy: Optional[str] = None,
        spread_margin_in_bp: Optional[float] = None,
        valuation_date: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.deposit_ccy1 = deposit_ccy1
        self.deposit_ccy2 = deposit_ccy2
        self.fx_swap_calculation_method = fx_swap_calculation_method
        self.fx_swaps_ccy1 = fx_swaps_ccy1
        self.fx_swaps_ccy1_ccy2 = fx_swaps_ccy1_ccy2
        self.fx_swaps_ccy2 = fx_swaps_ccy2
        self.fx_swaps_far_leg = fx_swaps_far_leg
        self.fx_swaps_near_leg = fx_swaps_near_leg
        self.price_side = price_side
        self.adjust_all_swap_points_to_cross_calendars = (
            adjust_all_swap_points_to_cross_calendars
        )
        self.calc_end_from_fwd_start = calc_end_from_fwd_start
        self.calc_end_from_pre_spot_start = calc_end_from_pre_spot_start
        self.ignore_ref_ccy_holidays = ignore_ref_ccy_holidays
        self.market_data_date = market_data_date
        self.one_day_values = one_day_values
        self.roll_over_time_policy = roll_over_time_policy
        self.spread_margin_in_bp = spread_margin_in_bp
        self.valuation_date = valuation_date

    @property
    def deposit_ccy1(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "depositCcy1")

    @deposit_ccy1.setter
    def deposit_ccy1(self, value):
        self._set_object_parameter(FxPoint, "depositCcy1", value)

    @property
    def deposit_ccy2(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "depositCcy2")

    @deposit_ccy2.setter
    def deposit_ccy2(self, value):
        self._set_object_parameter(FxPoint, "depositCcy2", value)

    @property
    def fx_swap_calculation_method(self):
        """
        The method we chose to price outright using or not implied deposits. Possible
        values are:   FxSwap (compute outright using swap points),
        DepositCcy1ImpliedFromFxSwap (compute currency1 deposits using swap points),
        DepositCcy2ImpliedFromFxSwap (compute currency2 deposits using swap points).
        Optional. Defaults to 'FxSwap'.
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
    def fx_swaps_ccy1(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "fxSwapsCcy1")

    @fx_swaps_ccy1.setter
    def fx_swaps_ccy1(self, value):
        self._set_object_parameter(FxPoint, "fxSwapsCcy1", value)

    @property
    def fx_swaps_ccy1_ccy2(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "fxSwapsCcy1Ccy2")

    @fx_swaps_ccy1_ccy2.setter
    def fx_swaps_ccy1_ccy2(self, value):
        self._set_object_parameter(FxPoint, "fxSwapsCcy1Ccy2", value)

    @property
    def fx_swaps_ccy2(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "fxSwapsCcy2")

    @fx_swaps_ccy2.setter
    def fx_swaps_ccy2(self, value):
        self._set_object_parameter(FxPoint, "fxSwapsCcy2", value)

    @property
    def fx_swaps_far_leg(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "fxSwapsFarLeg")

    @fx_swaps_far_leg.setter
    def fx_swaps_far_leg(self, value):
        self._set_object_parameter(FxPoint, "fxSwapsFarLeg", value)

    @property
    def fx_swaps_near_leg(self):
        """
        :return: object FxPoint
        """
        return self._get_object_parameter(FxPoint, "fxSwapsNearLeg")

    @fx_swaps_near_leg.setter
    def fx_swaps_near_leg(self, value):
        self._set_object_parameter(FxPoint, "fxSwapsNearLeg", value)

    @property
    def price_side(self):
        """
        The type of price returned for pricing Analysis:
        Bid(Bid value),
        Ask(Ask value),
        Mid(Mid value)
        Optional. Defaults to 'Mid'.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def adjust_all_swap_points_to_cross_calendars(self):
        """
        This flag define if cross-calendar holidays should be taken into account for
        fx_swaps_ccy1 and fx_swaps_ccy2. it adjusts swap points according to cross
        holidays if it's set to true, by default set to false.
        :return: bool
        """
        return self._get_parameter("adjustAllSwapPointsToCrossCalendars")

    @adjust_all_swap_points_to_cross_calendars.setter
    def adjust_all_swap_points_to_cross_calendars(self, value):
        self._set_parameter("adjustAllSwapPointsToCrossCalendars", value)

    @property
    def calc_end_from_fwd_start(self):
        """
        :return: bool
        """
        return self._get_parameter("calcEndFromFwdStart")

    @calc_end_from_fwd_start.setter
    def calc_end_from_fwd_start(self, value):
        self._set_parameter("calcEndFromFwdStart", value)

    @property
    def calc_end_from_pre_spot_start(self):
        """
        :return: bool
        """
        return self._get_parameter("calcEndFromPreSpotStart")

    @calc_end_from_pre_spot_start.setter
    def calc_end_from_pre_spot_start(self, value):
        self._set_parameter("calcEndFromPreSpotStart", value)

    @property
    def ignore_ref_ccy_holidays(self):
        """
        The reference currency holidays flag : When dates are computed, its possible to
        choose if holidays of the reference currency are included or not in the pricing
        Optional. Defaults to 'false'.
        :return: bool
        """
        return self._get_parameter("ignoreRefCcyHolidays")

    @ignore_ref_ccy_holidays.setter
    def ignore_ref_ccy_holidays(self, value):
        self._set_parameter("ignoreRefCcyHolidays", value)

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
    def one_day_values(self):
        """
        :return: str
        """
        return self._get_parameter("oneDayValues")

    @one_day_values.setter
    def one_day_values(self, value):
        self._set_parameter("oneDayValues", value)

    @property
    def roll_over_time_policy(self):
        """
        :return: str
        """
        return self._get_parameter("rollOverTimePolicy")

    @roll_over_time_policy.setter
    def roll_over_time_policy(self, value):
        self._set_parameter("rollOverTimePolicy", value)

    @property
    def spread_margin_in_bp(self):
        """
        If activated, it will calculate the indicated points in market data section
        instead of taking them directly from the curves
        :return: float
        """
        return self._get_parameter("spreadMarginInBp")

    @spread_margin_in_bp.setter
    def spread_margin_in_bp(self, value):
        self._set_parameter("spreadMarginInBp", value)

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
