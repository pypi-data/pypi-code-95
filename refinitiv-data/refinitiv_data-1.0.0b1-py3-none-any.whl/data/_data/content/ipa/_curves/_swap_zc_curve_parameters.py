# coding: utf8

__all__ = ["SwapZcCurveParameters"]

from typing import Optional

from ._forward_curve_types import Steps, Turns
from .._object_definition import ObjectDefinition

from ._enums import (
    DayCountBasis,
    InterpolationMode,
    CalendarAdjustment,
    PriceSide,
    CompoundingType,
    ExtrapolationMode,
)
from ._models import (
    ConvexityAdjustment,
    Step,
    Turn,
)
from ..._types import Strings, OptBool, OptStr
from ....tools import create_str_definition


class SwapZcCurveParameters(ObjectDefinition):
    """
    Parameters
    ----------
    interest_calculation_method : InterestCalculationMethod, optional
        Day count basis of the calculated zero coupon rates.
        Default value is: Dcb_Actual_Actual
    calendar_adjustment : CalendarAdjustment, optional
        Cash flow adjustment according to a calendar
        No:
        Null:
        Weekend: for cash flow pricing using the calendar
        WeekendCalendar: for cash flow pricing using the calendar defined
                         by the parameter 'calendars'.
    calendars : string, optional
        A list of one or more calendar codes used to define non-working days and to
        adjust coupon dates and values.
    compounding_type : CompoundingType, optional

    convexity_adjustment : ConvexityAdjustment, optional

    extrapolation_mode : ExtrapolationMode, optional
        None: no extrapolation
        Constant: constant extrapolation
        Linear: linear extrapolation
    interpolation_mode : InterpolationMode, optional
        Interpolation method used in swap zero curve bootstrap.
        Default value is: CubicSpline

        CubicDiscount: local cubic interpolation of discount factors
        CubicRate: local cubic interpolation of rates
        CubicSpline: a natural cubic spline
        Linear: linear interpolation
        Log: log linear interpolation
        ForwardMonotoneConvex
    price_side : SwapPriceSide, optional
        Defines which data is used for the rate surface computation.
        Default value is: Mid
    steps : Step, optional
        Use to calculate the swap rate surface discount curve, when OIS is selected as
        discount curve.
        The steps can specify overnight index stepped dates or/and rates.
    turns : Turn, optional
        Used to include end period rates/turns when calculating swap rate surfaces
    ignore_existing_definition : bool, optional

    reference_tenor : str, optional
        Root tenor(s) for the xIbor dependencies
    use_convexity_adjustment : bool, optional
        false / true
        Default value is: true.
        It indicates if the system needs to retrieve the convexity adjustment
    use_multi_dimensional_solver : bool, optional
        false / true
        Default value is: true.
        Specifies the use of the multi-dimensional solver for yield curve bootstrapping.
        This solving method is required because the bootstrapping method sometimes
        creates a ZC curve which does not accurately reprice the input instruments used
        to build it.
        The multi-dimensional solver is recommended when cubic interpolation methods
        are used in building the curve
        (in other cases, performance might be inferior to the regular bootstrapping
        method).
         - true: to use multi-dimensional solver for yield curve bootstrapping
         - false: not to use multi-dimensional solver for yield curve bootstrapping
    use_steps : bool, optional
        false / true
        Default value is: false.
        It indicates if the system needs to retrieve the overnight index
        stepped dates or/and rates
    valuation_date : str, optional
        The valuation date
        Default value is the current date
    """

    def __init__(
        self,
        interest_calculation_method: Optional[DayCountBasis] = None,
        calendar_adjustment: Optional[CalendarAdjustment] = None,
        calendars: Strings = None,
        compounding_type: Optional[CompoundingType] = None,
        convexity_adjustment: Optional[ConvexityAdjustment] = None,
        extrapolation_mode: Optional[ExtrapolationMode] = None,
        interpolation_mode: Optional[InterpolationMode] = None,
        price_side: Optional[PriceSide] = None,
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
        self.price_side = price_side
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
            end_path="forward_curve",
            name_class=self.__class__.__name__,
        )

    @property
    def calendar_adjustment(self):
        """
        Cash flow adjustment according to a calendar
        No:
        Null:
        Weekend: for cash flow pricing using the calendar
        WeekendCalendar: for cash flow pricing using the calendar defined
                         by the parameter 'calendars'.
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
        None: no extrapolation
        Constant: constant extrapolation
        Linear: linear extrapolation
        :return: enum ExtrapolationMode
        """
        return self._get_enum_parameter(ExtrapolationMode, "extrapolationMode")

    @extrapolation_mode.setter
    def extrapolation_mode(self, value):
        self._set_enum_parameter(ExtrapolationMode, "extrapolationMode", value)

    @property
    def interest_calculation_method(self):
        """
        Day count basis of the calculated zero coupon rates.
        Default value is: Dcb_Actual_Actual
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "interestCalculationMethod")

    @interest_calculation_method.setter
    def interest_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "interestCalculationMethod", value)

    @property
    def interpolation_mode(self):
        """
        Interpolation method used in swap zero curve bootstrap.
        Default value is: CubicSpline

        CubicDiscount: local cubic interpolation of discount factors
        CubicRate: local cubic interpolation of rates
        CubicSpline: a natural cubic spline
        Linear: linear interpolation
        Log: log linear interpolation
        ForwardMonotoneConvex
        :return: enum InterpolationMode
        """
        return self._get_enum_parameter(InterpolationMode, "interpolationMode")

    @interpolation_mode.setter
    def interpolation_mode(self, value):
        self._set_enum_parameter(InterpolationMode, "interpolationMode", value)

    @property
    def price_side(self):
        """
        Defines which data is used for the rate surface computation.
        Default value is: Mid
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def steps(self):
        """
        Use to calculate the swap rate surface discount curve, when OIS is selected as
        discount curve.
        The steps can specify overnight index stepped dates or/and rates.
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
        false / true
        Default value is: true.
        It indicates if the system needs to retrieve the convexity adjustment
        :return: bool
        """
        return self._get_parameter("useConvexityAdjustment")

    @use_convexity_adjustment.setter
    def use_convexity_adjustment(self, value):
        self._set_parameter("useConvexityAdjustment", value)

    @property
    def use_multi_dimensional_solver(self):
        """
        false / true
        Default value is: true.
        Specifies the use of the multi-dimensional solver for yield curve bootstrapping.
        This solving method is required because the bootstrapping method sometimes
        creates a ZC curve which does not accurately reprice the input instruments used
        to build it.
        The multi-dimensional solver is recommended when cubic interpolation methods
        are used in building the curve
        (in other cases, performance might be inferior to the regular bootstrapping
        method).
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
        false / true
        Default value is: false.
        It indicates if the system needs to retrieve the overnight index
        stepped dates or/and rates
        :return: bool
        """
        return self._get_parameter("useSteps")

    @use_steps.setter
    def use_steps(self, value):
        self._set_parameter("useSteps", value)

    @property
    def valuation_date(self):
        """
        The valuation date
        Default value is the current date
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
