# coding: utf8

__all__ = ["ZcCurveParameters"]

from typing import Optional
from ....tools import create_str_definition

from ._zc_curve_types import Steps, Turns
from .._object_definition import ObjectDefinition
from ._enums import (
    CalendarAdjustment,
    CompoundingType,
    ExtrapolationMode,
    DayCountBasis,
    MarketDataAccessDeniedFallback,
    SwapPriceSide,
    ZcInterpolationMode,
)
from ._models import Step, Turn, InterestRateCurveParameters, ConvexityAdjustment
from ..._types import OptBool, OptStr, Strings


class ZcCurveParameters(ObjectDefinition):
    """
    Parameters
    ----------
    interest_calculation_method : DayCountBasis, optional
        Day count basis of the calculated zero coupon rates
    calendar_adjustment : CalendarAdjustment, optional
        Cash flow adjustment according to a calendar.
        - No: for analytic pricing (i.e. from the bond structure)
        - Null: for cash flow pricing using the calendar null
        - Weekend: for cash flow pricing using the calendar weekend
        - Calendar: for cash flow pricing using the calendar defined
                    by the parameter calendars.
    calendars : string, optional
        A list of one or more calendar codes used to define non-working days and to
        adjust coupon dates and values.
    compounding_type : CompoundingType, optional
        Output rates yield type. Values can be:
        - Continuous: continuous rate (default value)
        - MoneyMarket: money market rate
        - Compounded: compounded rate
        - Discounted: discounted rate
    convexity_adjustment : ConvexityAdjustment, optional

    extrapolation_mode : ExtrapolationMode, optional
        Extrapolation method for the curve
        - None: no extrapolation
        - Constant: constant extrapolation
        - Linear: linear extrapolation
    interpolation_mode : ZcInterpolationMode, optional
        Interpolation method for the curve. Available values are:
        - CubicDiscount: local cubic interpolation of discount factors
        - CubicRate: local cubic interpolation of rates
        - CubicSpline: a natural cubic spline
        - ForwardMonotoneConvex: forward mMonotone Convexc interpolation
        - Linear: linear interpolation
        - Log: log-linear interpolation
        - Hermite: hermite (bessel) interpolation
        - AkimaMethod: the Akima method
            (a smoother variant of local cubic interpolation)
        - FritschButlandMethod: the Fritsch-Butland method (a monotonic cubic variant)
        - KrugerMethod: the Kruger method (a monotonic cubic variant)
        - MonotonicCubicNaturalSpline: a monotonic natural cubic spline
        - MonotonicHermiteCubic: monotonic hermite (Bessel) cubic interpolation
        - TensionSpline: a tension spline
    market_data_access_denied_fallback : MarketDataAccessDeniedFallback, optional
        - ReturnError: dont price the surface and return an error (Default value)
        - IgnoreConstituents: price the surface without the error market data
        - UseDelayedData: use delayed Market Data if possible
    pivot_curve_parameters : InterestRateCurveParameters, optional

    price_side : SwapPriceSide, optional
        Price side of the instrument to be used. default value is: mid
    reference_curve_parameters : InterestRateCurveParameters, optional

    steps : list of Step, optional

    turns : list of Turn, optional
        Used to include end period rates/turns when calculating swap rate surfaces
    ignore_existing_definition : bool, optional
        The curve definition is provided in the request, so ignore the one from data
        base
    reference_tenor : str, optional
        Root tenor(s) for the xIbor dependencies
    use_convexity_adjustment : bool, optional

    use_multi_dimensional_solver : bool, optional
        Specifies the use of the multi-dimensional solver for yield curve bootstrapping.
        This solving method is required because the bootstrapping method sometimes
        creates a ZC curve which does not accurately reprice the input instruments used
        to build it. The multi-dimensional solver is recommended when cubic
        interpolation methods are used in building the curve (in other cases,
        performance might be inferior to the regular bootstrapping method). When use for
        Credit Curve it is only used when the calibrationModel is set to Bootstrap.
        - true: to use multi-dimensional solver for yield curve bootstrapping
        - false: not to use multi-dimensional solver for yield curve bootstrapping
    use_steps : bool, optional

    valuation_date : str, optional
        The valuation date. The default value is the current date.
    """

    def __init__(
        self,
        interest_calculation_method: Optional[DayCountBasis] = None,
        calendar_adjustment: Optional[CalendarAdjustment] = None,
        calendars: Strings = None,
        compounding_type: Optional[CompoundingType] = None,
        convexity_adjustment: Optional[ConvexityAdjustment] = None,
        extrapolation_mode: Optional[ExtrapolationMode] = None,
        interpolation_mode: Optional[ZcInterpolationMode] = None,
        market_data_access_denied_fallback: Optional[
            MarketDataAccessDeniedFallback
        ] = None,
        pivot_curve_parameters: Optional[InterestRateCurveParameters] = None,
        price_side: Optional[SwapPriceSide] = None,
        reference_curve_parameters: Optional[InterestRateCurveParameters] = None,
        steps: Steps = None,
        turns: Turns = None,
        ignore_existing_definition: OptBool = None,
        reference_tenor: OptStr = None,
        use_convexity_adjustment: OptBool = None,
        use_multi_dimensional_solver: OptBool = None,
        use_steps: OptBool = None,
        valuation_date: OptStr = None,
    ) -> None:
        super().__init__()
        self.interest_calculation_method = interest_calculation_method
        self.calendar_adjustment = calendar_adjustment
        self.calendars = calendars
        self.compounding_type = compounding_type
        self.convexity_adjustment = convexity_adjustment
        self.extrapolation_mode = extrapolation_mode
        self.interpolation_mode = interpolation_mode
        self.market_data_access_denied_fallback = market_data_access_denied_fallback
        self.pivot_curve_parameters = pivot_curve_parameters
        self.price_side = price_side
        self.reference_curve_parameters = reference_curve_parameters
        self.steps = steps
        self.turns = turns
        self.ignore_existing_definition = ignore_existing_definition
        self.reference_tenor = reference_tenor
        self.use_convexity_adjustment = use_convexity_adjustment
        self.use_multi_dimensional_solver = use_multi_dimensional_solver
        self.use_steps = use_steps
        self.valuation_date = valuation_date

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.ipa.curves",
            end_path="zc_curve",
            name_class=self.__class__.__name__,
        )

    @property
    def calendar_adjustment(self):
        """
        Cash flow adjustment according to a calendar.
        - No: for analytic pricing (i.e. from the bond structure)
        - Null: for cash flow pricing using the calendar null
        - Weekend: for cash flow pricing using the calendar weekend
        - Calendar: for cash flow pricing using the calendar defined
                    by the parameter calendars.
        :return: enum CalendarAdjustment
        """
        return self._get_enum_parameter(CalendarAdjustment, "calendarAdjustment")

    @calendar_adjustment.setter
    def calendar_adjustment(self, value):
        self._set_enum_parameter(CalendarAdjustment, "calendarAdjustment", value)

    @property
    def calendars(self):
        """
        A list of one or more calendar codes used to define non-working days and to
        adjust coupon dates and values.
        :return: list string
        """
        return self._get_list_parameter(str, "calendars")

    @calendars.setter
    def calendars(self, value):
        self._set_list_parameter(str, "calendars", value)

    @property
    def compounding_type(self):
        """
        Output rates yield type. Values can be:
        - Continuous: continuous rate (default value)
        - MoneyMarket: money market rate
        - Compounded: compounded rate
        - Discounted: discounted rate
        :return: enum CompoundingType
        """
        return self._get_enum_parameter(CompoundingType, "compoundingType")

    @compounding_type.setter
    def compounding_type(self, value):
        self._set_enum_parameter(CompoundingType, "compoundingType", value)

    @property
    def convexity_adjustment(self):
        """
        :return: object ConvexityAdjustment
        """
        return self._get_object_parameter(ConvexityAdjustment, "convexityAdjustment")

    @convexity_adjustment.setter
    def convexity_adjustment(self, value):
        self._set_object_parameter(ConvexityAdjustment, "convexityAdjustment", value)

    @property
    def extrapolation_mode(self):
        """
        Extrapolation method for the curve
        - None: no extrapolation
        - Constant: constant extrapolation
        - Linear: linear extrapolation
        :return: enum ExtrapolationMode
        """
        return self._get_enum_parameter(ExtrapolationMode, "extrapolationMode")

    @extrapolation_mode.setter
    def extrapolation_mode(self, value):
        self._set_enum_parameter(ExtrapolationMode, "extrapolationMode", value)

    @property
    def interest_calculation_method(self):
        """
        Day count basis of the calculated zero coupon rates
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "interestCalculationMethod")

    @interest_calculation_method.setter
    def interest_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "interestCalculationMethod", value)

    @property
    def interpolation_mode(self):
        """
        Interpolation method for the curve.
        Available values are:
        - CubicDiscount: local cubic interpolation of discount factors
        - CubicRate: local cubic interpolation of rates
        - CubicSpline: a natural cubic spline
        - ForwardMonotoneConvex: forward mMonotone Convexc interpolation
        - Linear: linear interpolation
        - Log: log-linear interpolation
        - Hermite: Hermite (Bessel) interpolation
        - AkimaMethod: the Akima method (a smoother variant of local cubic interpolation)
        - FritschButlandMethod: the Fritsch-Butland method (a monotonic cubic variant)
        - KrugerMethod: the Kruger method (a monotonic cubic variant)
        - MonotonicCubicNaturalSpline: a monotonic natural cubic spline
        - MonotonicHermiteCubic: monotonic Hermite (Bessel) cubic interpolation
        - TensionSpline: a tension spline
        :return: enum ZcInterpolationMode
        """
        return self._get_enum_parameter(ZcInterpolationMode, "interpolationMode")

    @interpolation_mode.setter
    def interpolation_mode(self, value):
        self._set_enum_parameter(ZcInterpolationMode, "interpolationMode", value)

    @property
    def market_data_access_denied_fallback(self):
        """
        - ReturnError: dont price the surface and return an error (Default value)
        - IgnoreConstituents: price the surface without the error market data
        - UseDelayedData: use delayed Market Data if possible
        :return: enum MarketDataAccessDeniedFallback
        """
        return self._get_enum_parameter(
            MarketDataAccessDeniedFallback, "marketDataAccessDeniedFallback"
        )

    @market_data_access_denied_fallback.setter
    def market_data_access_denied_fallback(self, value):
        self._set_enum_parameter(
            MarketDataAccessDeniedFallback, "marketDataAccessDeniedFallback", value
        )

    @property
    def pivot_curve_parameters(self):
        """
        :return: object InterestRateCurveParameters
        """
        return self._get_object_parameter(
            InterestRateCurveParameters, "pivotCurveParameters"
        )

    @pivot_curve_parameters.setter
    def pivot_curve_parameters(self, value):
        self._set_object_parameter(
            InterestRateCurveParameters, "pivotCurveParameters", value
        )

    @property
    def price_side(self):
        """
        Price side of the instrument to be used. Default value is: Mid
        :return: enum SwapPriceSide
        """
        return self._get_enum_parameter(SwapPriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(SwapPriceSide, "priceSide", value)

    @property
    def reference_curve_parameters(self):
        """
        :return: object InterestRateCurveParameters
        """
        return self._get_object_parameter(
            InterestRateCurveParameters, "referenceCurveParameters"
        )

    @reference_curve_parameters.setter
    def reference_curve_parameters(self, value):
        self._set_object_parameter(
            InterestRateCurveParameters, "referenceCurveParameters", value
        )

    @property
    def steps(self):
        """
        :return: list Step
        """
        return self._get_list_parameter(Step, "steps")

    @steps.setter
    def steps(self, value):
        self._set_list_parameter(Step, "steps", value)

    @property
    def turns(self):
        """
        Used to include end period rates/turns when calculating swap rate surfaces
        :return: list Turn
        """
        return self._get_list_parameter(Turn, "turns")

    @turns.setter
    def turns(self, value):
        self._set_list_parameter(Turn, "turns", value)

    @property
    def ignore_existing_definition(self):
        """
        The curve definition is provided in the request, so ignore the one from data
        base
        :return: bool
        """
        return self._get_parameter("ignoreExistingDefinition")

    @ignore_existing_definition.setter
    def ignore_existing_definition(self, value):
        self._set_parameter("ignoreExistingDefinition", value)

    @property
    def reference_tenor(self):
        """
        Root tenor(s) for the xIbor dependencies
        :return: str
        """
        return self._get_parameter("referenceTenor")

    @reference_tenor.setter
    def reference_tenor(self, value):
        self._set_parameter("referenceTenor", value)

    @property
    def use_convexity_adjustment(self):
        """
        :return: bool
        """
        return self._get_parameter("useConvexityAdjustment")

    @use_convexity_adjustment.setter
    def use_convexity_adjustment(self, value):
        self._set_parameter("useConvexityAdjustment", value)

    @property
    def use_multi_dimensional_solver(self):
        """
        Specifies the use of the multi-dimensional solver for yield curve bootstrapping.
        This solving method is required because the bootstrapping method sometimes
        creates a ZC curve which does not accurately reprice the input instruments used
        to build it. The multi-dimensional solver is recommended when cubic
        interpolation methods are used in building the curve (in other cases,
        performance might be inferior to the regular bootstrapping method). When use for
        Credit Curve it is only used when the calibrationModel is set to Bootstrap.
        - true: to use multi-dimensional solver for yield curve bootstrapping
        - false: not to use multi-dimensional solver for yield curve bootstrapping
        :return: bool
        """
        return self._get_parameter("useMultiDimensionalSolver")

    @use_multi_dimensional_solver.setter
    def use_multi_dimensional_solver(self, value):
        self._set_parameter("useMultiDimensionalSolver", value)

    @property
    def use_steps(self):
        """
        :return: bool
        """
        return self._get_parameter("useSteps")

    @use_steps.setter
    def use_steps(self, value):
        self._set_parameter("useSteps", value)

    @property
    def valuation_date(self):
        """
        The valuation date. The default value is the current date.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
