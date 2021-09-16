# coding: utf8

__all__ = ["BondInstrumentDefinition"]

from typing import Optional

from ..instrument._instrument_definition import InstrumentDefinition
from ._enums import (
    DateRollingConvention,
    DayCountBasis,
    InterestType,
    StubRule,
    Frequency,
    AdjustInterestToPaymentDate,
    IndexCompoundingMethod,
    BusinessDayConvention,
    Direction,
)
from ._models import AmortizationItem


class BondInstrumentDefinition(InstrumentDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    instrument_code : str, optional
        Code to define the bond instrument. It can be an ISIN, a RIC, a CUSIP or an
        AssetId .
    end_date : str, optional
        Maturity date of the bond to override. Mandatory if instrument code has not been
        defined and is_perpetual flag has been set to false. In case an instrument code
        has been defined, value comes from bond reference data.
    direction : Direction, optional
        The direction of the leg. the possible values are:
        - 'Paid' (the cash flows of the leg are paid to the counterparty),
        - 'Received' (the cash flows of the leg are received from the counterparty).
          Optional for a single leg instrument (like a bond), in that case default value
          is Received. It is mandatory for a multi-instrument leg instrument (like Swap
          or CDS leg).
    interest_type : InterestType, optional
        A flag that indicates whether the leg is fixed or float. Possible values are:
        - 'Fixed' (the leg has a fixed coupon),
        - 'Float' (the leg has a floating rate index). Mandatory.
    notional_ccy : str, optional
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
    notional_amount : float, optional
        The notional amount of the leg at the period start date. Optional. By default
        1,000,000 is used.
    fixed_rate_percent : float, optional
        The fixed coupon rate in percentage. It is mandatory in case of a single leg
        instrument. Otherwise, in case of multi leg instrument, it can be computed as
        the Par rate.
    spread_bp : float, optional
        The spread in basis point that is added to the floating rate index index value.
        Optional. By default 0 is used.
    interest_payment_frequency : Frequency, optional
        The frequency of the interest payments. Optional if an instrument code/style
        have been defined : in that case, value comes from reference data. Otherwise, it
        is mandatory.
    interest_calculation_method : DayCountBasis, optional
        The Day Count Basis method used to calculate the coupon interest payments.
        Mandatory.
    accrued_calculation_method : DayCountBasis, optional
        The Day Count Basis method used to calculate the accrued interest payments.
        Optional. By default, the same value than interest_calculation_method is used.
    payment_business_day_convention : BusinessDayConvention, optional
        The method to adjust dates to a working day. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. In case an instrument code/style has been defined,
          value comes from bond reference data. Otherwise 'ModifiedFollowing' is used.
    payment_roll_convention : DateRollingConvention, optional
        Method to adjust payment dates when they fall at the end of the month (28th of
        February, 30th, 31st). The possible values are:
        - Last (For setting the calculated date to the last working day),
        - Same (For setting the calculated date to the same day . In this latter case,
          the date may be moved according to the date moving convention if it is a
          non-working day),
        - Last28 (For setting the calculated date to the last working day. 28FEB being
          always considered as the last working day),
        - Same28 (For setting the calculated date to the same day .28FEB being always
          considered as the last working day). Optional. In case an instrument code has
          been defined, value comes from bond reference data. Otherwise, 'SameDay' is
          used.
    index_reset_frequency : Frequency, optional
        The reset frequency in case the leg Type is Float. Optional. By default the
        IndexTenor is used.
    index_fixing_lag : int, optional
        Defines the number of working days between the fixing date and the start of the
        coupon period ('InAdvance') or the end of the coupon period ('InArrears').
        Optional. By default 0 is used.
    first_regular_payment_date : str, optional
        The first regular coupon payment date for leg with an odd first coupon.
        Optional.
    last_regular_payment_date : str, optional
        The last regular coupon payment date for leg with an odd last coupon. Optional.
    amortization_schedule : AmortizationItem, optional
        Definition of amortizations
    payment_business_days : str, optional
        A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
        Optional. By default the calendar associated to notional_ccy is used.
    adjust_interest_to_payment_date : AdjustInterestToPaymentDate, optional
        A flag that indicates if the coupon dates are adjusted to the payment dates.
        Optional. By default 'false' is used.
    index_compounding_method : IndexCompoundingMethod, optional
        A flag that defines how the coupon rate is calculated from the reset floating
        rates when the reset frequency is higher than the interest payment frequency
        (e.g. daily index reset with quarterly interest payment). The possible values
        are:
        - Compounded (uses the compounded average rate from multiple fixings),
        - Average (uses the arithmetic average rate from multiple fixings),
        - Constant (uses the last published rate among multiple fixings),
        - AdjustedCompounded (uses Chinese 7-day repo fixing),
        - MexicanCompounded (uses Mexican Bremse fixing). Optional. By default
          'Constant' is used.
    interest_payment_delay : int, optional
        The number of working days between the end of coupon period and the actual
        interest payment date. Optional. By default no delay (0) is applied.
    stub_rule : StubRule, optional
        The rule that defines whether coupon roll dates are aligned on the  maturity or
        the issue date.  The possible values are:
        - ShortFirstProRata (to create a short period between the start date and the
          first coupon date, and pay a smaller amount of interest for the short
          period.All coupon dates are calculated backward from the maturity date),
        - ShortFirstFull (to create a short period between the start date and the first
          coupon date, and pay a regular coupon on the first coupon date. All coupon
          dates are calculated backward from the maturity date),
        - LongFirstFull (to create a long period between the start date and the second
          coupon date, and pay a regular coupon on the second coupon date. All coupon
          dates are calculated backward from the maturity date),
        - ShortLastProRata (to create a short period between the last payment date and
          maturity, and pay a smaller amount of interest for the short period. All
          coupon dates are calculated forward from the start date). This property may
          also be used in conjunction with first_regular_payment_date and
          last_regular_payment_date; in that case the following values can be defined:
        - Issue (all dates are aligned on the issue date),
        - Maturity (all dates are aligned on the maturity date). Optional. By default
          'Maturity' is used.
    issue_date : str, optional
        Date of issuance of the bond to override. Mandatory if instrument code has not
        been defined. In case an instrument code has been defined, value comes from bond
        reference data.
    first_accrual_date : str, optional
        Date at which bond starts accruing. Optional. In case an instrument code has
        been defined, value comes from bond reference data. Otherwise default value is
        the issue date of the bond.
    index_fixing_ric : str, optional
        The RIC that carries the fixing value. This value overrides the RIC associated
        by default with the IndexName and IndexTenor. Optional.
    is_perpetual : bool, optional
        Flag the defines wether the bond is perpetual or not in case of user defined
        bond. Optional. In case an instrument code has been defined, value comes from
        bond reference data. In case of user defined bond, default value is 'false'.
    template : str, optional
        A reference to a Adfin instrument contract or the Adfin detailed contract.
        Optional. Either instrument_code, template, or full definition must be provided.
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        instrument_code: Optional[str] = None,
        end_date: Optional[str] = None,
        direction: Optional[Direction] = None,
        interest_type: Optional[InterestType] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        fixed_rate_percent: Optional[float] = None,
        spread_bp: Optional[float] = None,
        interest_payment_frequency: Optional[Frequency] = None,
        interest_calculation_method: Optional[DayCountBasis] = None,
        accrued_calculation_method: Optional[DayCountBasis] = None,
        payment_business_day_convention: Optional[BusinessDayConvention] = None,
        payment_roll_convention: Optional[DateRollingConvention] = None,
        index_reset_frequency: Optional[Frequency] = None,
        index_fixing_lag: Optional[int] = None,
        first_regular_payment_date: Optional[str] = None,
        last_regular_payment_date: Optional[str] = None,
        amortization_schedule: Optional[AmortizationItem] = None,
        payment_business_days: Optional[str] = None,
        adjust_interest_to_payment_date: Optional[AdjustInterestToPaymentDate] = None,
        index_compounding_method: Optional[IndexCompoundingMethod] = None,
        interest_payment_delay: Optional[int] = None,
        stub_rule: Optional[StubRule] = None,
        issue_date: Optional[str] = None,
        first_accrual_date: Optional[str] = None,
        index_fixing_ric: Optional[str] = None,
        is_perpetual: Optional[bool] = None,
        template: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.instrument_tag = instrument_tag
        self.instrument_code = instrument_code
        self.end_date = end_date
        self.direction = direction
        self.interest_type = interest_type
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.fixed_rate_percent = fixed_rate_percent
        self.spread_bp = spread_bp
        self.interest_payment_frequency = interest_payment_frequency
        self.interest_calculation_method = interest_calculation_method
        self.accrued_calculation_method = accrued_calculation_method
        self.payment_business_day_convention = payment_business_day_convention
        self.payment_roll_convention = payment_roll_convention
        self.index_reset_frequency = index_reset_frequency
        self.index_fixing_lag = index_fixing_lag
        self.first_regular_payment_date = first_regular_payment_date
        self.last_regular_payment_date = last_regular_payment_date
        self.amortization_schedule = amortization_schedule
        self.payment_business_days = payment_business_days
        self.adjust_interest_to_payment_date = adjust_interest_to_payment_date
        self.index_compounding_method = index_compounding_method
        self.interest_payment_delay = interest_payment_delay
        self.stub_rule = stub_rule
        self.issue_date = issue_date
        self.first_accrual_date = first_accrual_date
        self.index_fixing_ric = index_fixing_ric
        self.is_perpetual = is_perpetual
        self.template = template

    @classmethod
    def get_instrument_type(cls):
        return "Bond"

    @property
    def accrued_calculation_method(self):
        """
        The Day Count Basis method used to calculate the accrued interest payments.
        Optional. By default, the same value than InterestCalculationMethod is used.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "accruedCalculationMethod")

    @accrued_calculation_method.setter
    def accrued_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "accruedCalculationMethod", value)

    @property
    def adjust_interest_to_payment_date(self):
        """
        A flag that indicates if the coupon dates are adjusted to the payment dates.
        Optional. By default 'false' is used.
        :return: enum AdjustInterestToPaymentDate
        """
        return self._get_enum_parameter(
            AdjustInterestToPaymentDate, "adjustInterestToPaymentDate"
        )

    @adjust_interest_to_payment_date.setter
    def adjust_interest_to_payment_date(self, value):
        self._set_enum_parameter(
            AdjustInterestToPaymentDate, "adjustInterestToPaymentDate", value
        )

    @property
    def amortization_schedule(self):
        """
        Definition of amortizations
        :return: list AmortizationItem
        """
        return self._get_list_parameter(AmortizationItem, "amortizationSchedule")

    @amortization_schedule.setter
    def amortization_schedule(self, value):
        self._set_list_parameter(AmortizationItem, "amortizationSchedule", value)

    @property
    def direction(self):
        """
        The direction of the leg. the possible values are:
        - 'Paid' (the cash flows of the leg are paid to the counterparty),
        - 'Received' (the cash flows of the leg are received from the counterparty).
          Optional for a single leg instrument (like a bond), in that case default value
          is Received. It is mandatory for a multi-instrument leg instrument (like Swap
          or CDS leg).
        :return: enum Direction
        """
        return self._get_enum_parameter(Direction, "direction")

    @direction.setter
    def direction(self, value):
        self._set_enum_parameter(Direction, "direction", value)

    @property
    def index_compounding_method(self):
        """
        A flag that defines how the coupon rate is calculated from the reset floating
        rates when the reset frequency is higher than the interest payment frequency
        (e.g. daily index reset with quarterly interest payment). The possible values
        are:
        - Compounded (uses the compounded average rate from multiple fixings),
        - Average (uses the arithmetic average rate from multiple fixings),
        - Constant (uses the last published rate among multiple fixings),
        - AdjustedCompounded (uses Chinese 7-day repo fixing),
        - MexicanCompounded (uses Mexican Bremse fixing). Optional. By default
          'Constant' is used.
        :return: enum IndexCompoundingMethod
        """
        return self._get_enum_parameter(
            IndexCompoundingMethod, "indexCompoundingMethod"
        )

    @index_compounding_method.setter
    def index_compounding_method(self, value):
        self._set_enum_parameter(
            IndexCompoundingMethod, "indexCompoundingMethod", value
        )

    @property
    def index_reset_frequency(self):
        """
        The reset frequency in case the leg Type is Float. Optional. By default the
        IndexTenor is used.
        :return: enum Frequency
        """
        return self._get_enum_parameter(Frequency, "indexResetFrequency")

    @index_reset_frequency.setter
    def index_reset_frequency(self, value):
        self._set_enum_parameter(Frequency, "indexResetFrequency", value)

    @property
    def interest_calculation_method(self):
        """
        The Day Count Basis method used to calculate the coupon interest payments.
        Mandatory.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "interestCalculationMethod")

    @interest_calculation_method.setter
    def interest_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "interestCalculationMethod", value)

    @property
    def interest_payment_frequency(self):
        """
        The frequency of the interest payments. Optional if an instrument code/style
        have been defined : in that case, value comes from reference data. Otherwise, it
        is mandatory.
        :return: enum Frequency
        """
        return self._get_enum_parameter(Frequency, "interestPaymentFrequency")

    @interest_payment_frequency.setter
    def interest_payment_frequency(self, value):
        self._set_enum_parameter(Frequency, "interestPaymentFrequency", value)

    @property
    def interest_type(self):
        """
        A flag that indicates whether the leg is fixed or float. Possible values are:
        - 'Fixed' (the leg has a fixed coupon),
        - 'Float' (the leg has a floating rate index). Mandatory.
        :return: enum InterestType
        """
        return self._get_enum_parameter(InterestType, "interestType")

    @interest_type.setter
    def interest_type(self, value):
        self._set_enum_parameter(InterestType, "interestType", value)

    @property
    def payment_business_day_convention(self):
        """
        The method to adjust dates to a working day. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. In case an instrument code/style has been defined,
          value comes from bond reference data. Otherwise 'ModifiedFollowing' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "paymentBusinessDayConvention"
        )

    @payment_business_day_convention.setter
    def payment_business_day_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "paymentBusinessDayConvention", value
        )

    @property
    def payment_roll_convention(self):
        """
        Method to adjust payment dates when they fall at the end of the month (28th of
        February, 30th, 31st). The possible values are:
        - Last (For setting the calculated date to the last working day),
        - Same (For setting the calculated date to the same day . In this latter case,
          the date may be moved according to the date moving convention if it is a
          non-working day),
        - Last28 (For setting the calculated date to the last working day. 28FEB being
          always considered as the last working day),
        - Same28 (For setting the calculated date to the same day .28FEB being always
          considered as the last working day). Optional. In case an instrument code has
          been defined, value comes from bond reference data. Otherwise, 'SameDay' is
          used.
        :return: enum DateRollingConvention
        """
        return self._get_enum_parameter(DateRollingConvention, "paymentRollConvention")

    @payment_roll_convention.setter
    def payment_roll_convention(self, value):
        self._set_enum_parameter(DateRollingConvention, "paymentRollConvention", value)

    @property
    def stub_rule(self):
        """
        The rule that defines whether coupon roll dates are aligned on the  maturity or
        the issue date.  The possible values are:
        - ShortFirstProRata (to create a short period between the start date and the
          first coupon date, and pay a smaller amount of interest for the short
          period.All coupon dates are calculated backward from the maturity date),
        - ShortFirstFull (to create a short period between the start date and the first
          coupon date, and pay a regular coupon on the first coupon date. All coupon
          dates are calculated backward from the maturity date),
        - LongFirstFull (to create a long period between the start date and the second
          coupon date, and pay a regular coupon on the second coupon date. All coupon
          dates are calculated backward from the maturity date),
        - ShortLastProRata (to create a short period between the last payment date and
          maturity, and pay a smaller amount of interest for the short period. All
          coupon dates are calculated forward from the start date). This property may
          also be used in conjunction with firstRegularPaymentDate and
          lastRegularPaymentDate; in that case the following values can be defined:
        - Issue (all dates are aligned on the issue date),
        - Maturity (all dates are aligned on the maturity date). Optional. By default
          'Maturity' is used.
        :return: enum StubRule
        """
        return self._get_enum_parameter(StubRule, "stubRule")

    @stub_rule.setter
    def stub_rule(self, value):
        self._set_enum_parameter(StubRule, "stubRule", value)

    @property
    def end_date(self):
        """
        Maturity date of the bond to override. Mandatory if instrument code has not been
        defined and is_perpetual flag has been set to false. In case an instrument code
        has been defined, value comes from bond reference data.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def first_accrual_date(self):
        """
        Date at which bond starts accruing. Optional. In case an instrument code has
        been defined, value comes from bond reference data. Otherwise default value is
        the issue date of the bond.
        :return: str
        """
        return self._get_parameter("firstAccrualDate")

    @first_accrual_date.setter
    def first_accrual_date(self, value):
        self._set_parameter("firstAccrualDate", value)

    @property
    def first_regular_payment_date(self):
        """
        The first regular coupon payment date for leg with an odd first coupon.
        Optional.
        :return: str
        """
        return self._get_parameter("firstRegularPaymentDate")

    @first_regular_payment_date.setter
    def first_regular_payment_date(self, value):
        self._set_parameter("firstRegularPaymentDate", value)

    @property
    def fixed_rate_percent(self):
        """
        The fixed coupon rate in percentage. It is mandatory in case of a single leg
        instrument. Otherwise, in case of multi leg instrument, it can be computed as
        the Par rate.
        :return: float
        """
        return self._get_parameter("fixedRatePercent")

    @fixed_rate_percent.setter
    def fixed_rate_percent(self, value):
        self._set_parameter("fixedRatePercent", value)

    @property
    def index_fixing_lag(self):
        """
        Defines the number of working days between the fixing date and the start of the
        coupon period ('InAdvance') or the end of the coupon period ('InArrears').
        Optional. By default 0 is used.
        :return: int
        """
        return self._get_parameter("indexFixingLag")

    @index_fixing_lag.setter
    def index_fixing_lag(self, value):
        self._set_parameter("indexFixingLag", value)

    @property
    def index_fixing_ric(self):
        """
        The RIC that carries the fixing value. This value overrides the RIC associated
        by default with the IndexName and IndexTenor. Optional.
        :return: str
        """
        return self._get_parameter("indexFixingRic")

    @index_fixing_ric.setter
    def index_fixing_ric(self, value):
        self._set_parameter("indexFixingRic", value)

    @property
    def instrument_code(self):
        """
        Code to define the bond instrument. It can be an ISIN, a RIC, a CUSIP or an
        AssetId .
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def interest_payment_delay(self):
        """
        The number of working days between the end of coupon period and the actual
        interest payment date. Optional. By default no delay (0) is applied.
        :return: int
        """
        return self._get_parameter("interestPaymentDelay")

    @interest_payment_delay.setter
    def interest_payment_delay(self, value):
        self._set_parameter("interestPaymentDelay", value)

    @property
    def is_perpetual(self):
        """
        Flag the defines wether the bond is perpetual or not in case of user defined
        bond. Optional. In case an instrument code has been defined, value comes from
        bond reference data. In case of user defined bond, default value is 'false'.
        :return: bool
        """
        return self._get_parameter("isPerpetual")

    @is_perpetual.setter
    def is_perpetual(self, value):
        self._set_parameter("isPerpetual", value)

    @property
    def issue_date(self):
        """
        Date of issuance of the bond to override. Mandatory if instrument code has not
        been defined. In case an instrument code has been defined, value comes from bond
        reference data.
        :return: str
        """
        return self._get_parameter("issueDate")

    @issue_date.setter
    def issue_date(self, value):
        self._set_parameter("issueDate", value)

    @property
    def last_regular_payment_date(self):
        """
        The last regular coupon payment date for leg with an odd last coupon. Optional.
        :return: str
        """
        return self._get_parameter("lastRegularPaymentDate")

    @last_regular_payment_date.setter
    def last_regular_payment_date(self, value):
        self._set_parameter("lastRegularPaymentDate", value)

    @property
    def notional_amount(self):
        """
        The notional amount of the leg at the period start date. Optional. By default
        1,000,000 is used.
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def notional_ccy(self):
        """
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
        :return: str
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        self._set_parameter("notionalCcy", value)

    @property
    def payment_business_days(self):
        """
        A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
        Optional. By default the calendar associated to notional_ccy is used.
        :return: str
        """
        return self._get_parameter("paymentBusinessDays")

    @payment_business_days.setter
    def payment_business_days(self, value):
        self._set_parameter("paymentBusinessDays", value)

    @property
    def spread_bp(self):
        """
        The spread in basis point that is added to the floating rate index index value.
        Optional. By default 0 is used.
        :return: float
        """
        return self._get_parameter("spreadBp")

    @spread_bp.setter
    def spread_bp(self, value):
        self._set_parameter("spreadBp", value)

    @property
    def template(self):
        """
        A reference to a Adfin instrument contract or the Adfin detailed contract.
        Optional. Either instrument_code, template, or full definition must be provided.
        :return: str
        """
        return self._get_parameter("template")

    @template.setter
    def template(self, value):
        self._set_parameter("template", value)
