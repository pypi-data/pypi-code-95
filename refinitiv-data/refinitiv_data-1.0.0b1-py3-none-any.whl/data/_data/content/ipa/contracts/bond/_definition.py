# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Iterable, Union

from . import PricingParameters
from ._bond_definition import BondInstrumentDefinition
from ._enums import (
    AdjustInterestToPaymentDate,
    BusinessDayConvention,
    DayCountBasis,
    Direction,
    Frequency,
    IndexCompoundingMethod,
    InterestType,
    DateRollingConvention,
    StubRule,
)
from ._models import AmortizationItem
from .._outputs import Outputs
from .._base_definition import BaseDefinition


class Definition(BaseDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_code : str, optional
        Code to define the bond instrument.
    instrument_tag : str, optional
        User defined string to identify the instrument. It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported.
    end_date : str, optional
        Maturity date of the bond to override. Mandatory if instrument code has not been
        defined and is_perpetual flag has been set to false. In case an instrument code
        has been defined, value comes from bond reference data.
    direction : Direction, optional
        The direction of the leg. Optional for a single leg instrument (like a bond),
        in that case default value is Received. It is mandatory for a multi-instrument
        leg instrument (like Swap or CDS leg).
    interest_type : InterestType, optional
        A flag that indicates whether the leg is fixed or float.
    notional_ccy : str, optional
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
    notional_amount : float, optional
        The notional amount of the leg at the period start date.
        By default 1,000,000 is used.
    fixed_rate_percent : float, optional
        The fixed coupon rate in percentage. It is mandatory in case of a single leg
        instrument. Otherwise, in case of multi leg instrument, it can be computed as
        the Par rate.
    spread_bp : float, optional
        The spread in basis point that is added to the floating rate index index value.
        By default 0 is used.
    interest_payment_frequency : Frequency or str, optional
        The frequency of the interest payments. Optional if an instrument code/style
        have been defined : in that case, value comes from reference data. Otherwise, it
        is mandatory.
    interest_calculation_method : DayCountBasis or str, optional
        The Day Count Basis method used to calculate the coupon interest payments.
    accrued_calculation_method : DayCountBasis, optional
        The Day Count Basis method used to calculate the accrued interest payments.
        By default, the same value than interest_calculation_method is used.
    payment_business_day_convention : BusinessDayConvention, optional
        The method to adjust dates to a working day.
        In case an instrument code/style has been defined, value comes from bond
        reference data. Otherwise 'ModifiedFollowing' is used.
    payment_roll_convention : DateRollingConvention, optional
        Method to adjust payment dates when they fall at the end of the month (28th of
        February, 30th, 31st). In case an instrument code has been defined,
        value comes from bond reference data. Otherwise, 'SameDay' is used.
    index_reset_frequency : Frequency, optional
        The reset frequency in case the leg Type is Float.
        By default, the IndexTenor is used.
    index_fixing_lag : int, optional
        Defines the number of working days between the fixing date and the start of the
        coupon period ('InAdvance') or the end of the coupon period ('InArrears').
        By default 0 is used.
    first_regular_payment_date : str, optional
        The first regular coupon payment date for leg with an odd first coupon.
    last_regular_payment_date : str, optional
        The last regular coupon payment date for leg with an odd last coupon.
    amortization_schedule : AmortizationItem, optional
        Definition of amortizations.
    payment_business_days : str, optional
        A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
        By default the calendar associated to notional_ccy is used.
    adjust_interest_to_payment_date : AdjustInterestToPaymentDate, optional
        A flag that indicates if the coupon dates are adjusted to the payment dates.
        By default 'false' is used.
    index_compounding_method : IndexCompoundingMethod, optional
        A flag that defines how the coupon rate is calculated from the reset floating
        rates when the reset frequency is higher than the interest payment frequency
        (e.g. daily index reset with quarterly interest payment).
        By default 'Constant' is used.
    interest_payment_delay : int, optional
        The number of working days between the end of coupon period and the actual
        interest payment date.
        By default no delay (0) is applied.
    stub_rule : StubRule, optional
        The rule that defines whether coupon roll dates are aligned on the  maturity or
        the issue date.
        By default 'Maturity' is used.
    issue_date : str, optional
        Date of issuance of the bond to override. Mandatory if instrument code has not
        been defined. In case an instrument code has been defined, value comes from bond
        reference data.
    first_accrual_date : str, optional
        Date at which bond starts accruing. In case an instrument code has
        been defined, value comes from bond reference data. Otherwise default value is
        the issue date of the bond.
    index_fixing_ric : str, optional
        The RIC that carries the fixing value. This value overrides the RIC associated
        by default with the IndexName and IndexTenor.
    is_perpetual : bool, optional
        Flag the defines wether the bond is perpetual or not in case of user defined
        bond. In case an instrument code has been defined, value comes from
        bond reference data. In case of user defined bond, default value is 'false'.
    template : str, optional
        A reference to a Adfin instrument contract or the Adfin detailed contract.
        Either instrument_code, template, or full definition must be provided.
    fields: list of str, optional
        Contains the list of Analytics that the quantitative analytic service will
        compute.
    pricing_parameters : PricingParameters, optional
        The pricing parameters to apply to this instrument. If pricing
        parameters are not provided at this level parameters defined globally at the
        request level are used. If no pricing parameters are provided globally default
        values apply.
    outputs: list of (str or Outputs), optional
        Contains the sections that will be returned by the API.
    extended_params : dict, optional
        If necessary other parameters.

    Methods
    -------
    get_data(session=session, on_response=on_response)
        Returns a response to the data platform
    get_data_async(session=None, on_response=None, async_mode=None)
        Returns a response asynchronously to the data platform
    get_stream(session=session, api="")
        Get stream quantitative analytic service subscription

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> definition = rdf.bond.Definition(
     ...    issue_date = "2002-02-28",
     ...    end_date = "2032-02-28",
     ...    notional_ccy = "USD",
     ...    interest_payment_frequency = "Annual",
     ...    fixed_rate_percent = 7,
     ...    interest_calculation_method = rdf.bond.DayCountBasis.DCB_ACTUAL_ACTUAL
     ...)
     >>> response = definition.get_data()

     Using get_data_async
     >>> import asyncio
     >>> task = asyncio.gather(
     ...    definition.get_data_async(),
     ...)
     >>> asyncio.get_event_loop().run_until_complete(task)
     >>> response, *_ = task._result

     Using get_stream
     >>> response = definition.get_stream()
    """

    def __init__(
        self,
        instrument_code: Optional[str] = None,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        direction: Optional[Direction] = None,
        interest_type: Optional[InterestType] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        fixed_rate_percent: Optional[float] = None,
        spread_bp: Optional[float] = None,
        interest_payment_frequency: Union[Frequency, str] = None,
        interest_calculation_method: Union[DayCountBasis, str] = None,
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
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ) -> None:
        definition = BondInstrumentDefinition(
            accrued_calculation_method=accrued_calculation_method,
            adjust_interest_to_payment_date=adjust_interest_to_payment_date,
            amortization_schedule=amortization_schedule,
            direction=direction,
            index_compounding_method=index_compounding_method,
            index_reset_frequency=index_reset_frequency,
            interest_calculation_method=interest_calculation_method,
            interest_payment_frequency=interest_payment_frequency,
            interest_type=interest_type,
            payment_business_day_convention=payment_business_day_convention,
            payment_roll_convention=payment_roll_convention,
            stub_rule=stub_rule,
            end_date=end_date,
            first_accrual_date=first_accrual_date,
            first_regular_payment_date=first_regular_payment_date,
            fixed_rate_percent=fixed_rate_percent,
            index_fixing_lag=index_fixing_lag,
            index_fixing_ric=index_fixing_ric,
            instrument_code=instrument_code,
            instrument_tag=instrument_tag,
            interest_payment_delay=interest_payment_delay,
            is_perpetual=is_perpetual,
            issue_date=issue_date,
            last_regular_payment_date=last_regular_payment_date,
            notional_amount=notional_amount,
            notional_ccy=notional_ccy,
            payment_business_days=payment_business_days,
            spread_bp=spread_bp,
            template=template,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )
