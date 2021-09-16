# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Iterable, Union

from . import PricingParameters
from .._outputs import Outputs
from .._base_definition import BaseDefinition
from ._cap_floor_definition import CapFloorInstrumentDefinition
from ._enums import (
    AdjustInterestToPaymentDate,
    IndexResetType,
    Frequency,
    DateRollingConvention,
    DayCountBasis,
    StubRule,
    BuySell,
    BusinessDayConvention,
)
from ._models import (
    AmortizationItem,
    BarrierDefinitionElement,
)


class Definition(BaseDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    start_date : str, optional
        The option start date
    end_date : str, optional
        The maturity date of the CapFloor
    tenor : str, optional
        Tenor of the option
    notional_ccy : str, optional
        The ISO code of the notional currency. Mandatory if instrument code or
        instrument style has not been defined. In case an instrument code/style has been
        defined, value may comes from the reference data.
    notional_amount : float, optional
        The notional amount of the leg at the period start date. Optional. By default
        1,000,000 is used.
    index_name : str, optional
        The name of the floating rate index.
    index_tenor : str, optional
        The period code that represents the maturity of the floating rate index.
        Mandatory when the leg is float.
    interest_payment_frequency : Frequency, optional
        The frequency of the interest payments. Optional if an instrument code/style
        have been defined : in that case, value comes from reference data. Otherwise, it
        is mandatory.
    interest_calculation_method : DayCountBasis, str, optional
        The Day Count Basis method used to calculate the coupon interest payments.
        Mandatory.
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
        The method to adjust payment dates whn they fall at the end of the month (28th
        of February, 30th, 31st). The possible values are:
        - Last (For setting the calculated date to the last working day),
        - Same (For setting the calculated date to the same day . In this latter case,
          the date may be moved according to the date moving convention if it is a
          non-working day),
        - Last28 (For setting the calculated date to the last working day. 28FEB being
          always considered as the last working day),
        - Same28 (For setting the calculated date to the same day .28FEB being always
          considered as the last working day). Optional. By default 'SameDay' is used.
    index_reset_frequency : Frequency, optional
        The reset frequency in case the leg Type is Float. Optional. By default the
        IndexTenor is used.
    index_reset_type : IndexResetType, optional
        A flag that indicates if the floating rate index is reset before the coupon
        period starts or at the end of the coupon period. The possible values are:
        - InAdvance (resets the index before the start of the interest period),
        - InArrears (resets the index at the end of the interest period). Optional. By
          default 'InAdvance' is used.
    index_fixing_lag : int, optional
        Defines the positive number of working days between the fixing date and the
        start of the coupon period ('InAdvance') or the end of the coupon period
        ('InArrears'). Optional. By default 0 is used.
    amortization_schedule : list of AmortizationItem, optional
        Definition of amortizations
    payment_business_days : str, optional
        A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
        Optional. By default the calendar associated to NotionalCcy is used.
    adjust_interest_to_payment_date : AdjustInterestToPaymentDate, optional
        A flag that indicates if the coupon dates are adjusted to the payment dates.
        Optional. By default 'false' is used.
    stub_rule : StubRule, optional
        The rule that defines whether coupon roll dates are aligned on the  maturity or
        the issue date. The possible values are:
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
    barrier_definition : BarrierDefinitionElement, optional

    buy_sell : BuySell, optional
        The side of the deal. Possible values:
        - Buy
        - Sell
    annualized_rebate : bool, optional

    cap_digital_payout_percent : float, optional

    cap_strike_percent : float, optional
        Cap leg strike expressed in %
    cms_template : str, optional
        A reference to a common swap contract that represents the underlying swap in
        case of a Constant Maturity Swap contract (CMS). Mandatory for CMS contract.
    floor_digital_payout_percent : float, optional

    floor_strike_percent : float, optional
        Floor leg strike expressed in %
    index_fixing_ric : str, optional
        The RIC that carries the fixing value. This value overrides the RIC associated
        by default with the IndexName and IndexTenor. Optional.
    fields: list of str, optional
        Contains the list of Analytics that the quantitative analytic service will
        compute.
    pricing_parameters : PricingParameters, optional
        The pricing parameters to apply to this instrument. Optional. If pricing
        parameters are not provided at this level parameters defined globally at the
        request level are used. If no pricing parameters are provided globally default
        values apply.
    outputs: list of str, list of Outputs, optional
        Contains the sections that will be returned by the API
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_data(session=session, on_response=on_response)
        Returns a response to the data platform
    get_stream(session=session, api="")
        Get stream object of this definition

    Examples
    --------
    >>> import refinitiv.data.content.ipa.financial_contracts as rdf
    >>> definition = rdf.cap_floor.Definition(
    ...    instrument_tag="CapOnCms",
    ...    stub_rule=rdf.cap_floor.StubRule.MATURITY,
    ...    notional_ccy="USD",
    ...    start_date="2018-06-15",
    ...    end_date="2022-06-15",
    ...    notional_amount=1000000,
    ...    index_name="Composite",
    ...    index_tenor="5Y",
    ...    interest_calculation_method="Dcb_Actual_360",
    ...    interest_payment_frequency=rdf.cap_floor.Frequency.QUARTERLY,
    ...    buy_sell=rdf.cap_floor.BuySell.BUY,
    ...    cap_strike_percent=1,
    ...    pricing_parameters=rdf.cap_floor.PricingParameters(
    ...        skip_first_cap_floorlet=False, valuation_date="2020-02-07"
    ...    ),
    ...    outputs=[
    ...        rdf.Outputs.DATA,
    ...        rdf.Outputs.MARKET_DATA,
    ...    ],
    ...    fields=[
    ...        "InstrumentTag",
    ...        "InstrumentDescription",
    ...        "StartDate",
    ...        "EndDate",
    ...        "InterestPaymentFrequency",
    ...        "IndexRic",
    ...        "CapStrikePercent",
    ...        "FloorStrikePercent",
    ...        "NotionalCcy",
    ...        "NotionalAmount",
    ...        "PremiumBp",
    ...        "PremiumPercent",
    ...        "MarketValueInDealCcy",
    ...        "MarketValueInReportCcy",
    ...        "ErrorMessage",
    ...    ],
    ...)
    >>> response = definition.get_data()

     Using get_stream
     >>> response = definition.get_stream()
    """

    def __init__(
        self,
        *,
        instrument_tag: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        index_name: Optional[str] = None,
        index_tenor: Optional[str] = None,
        interest_payment_frequency: Union[Frequency, str] = None,
        interest_calculation_method: Union[DayCountBasis, str] = None,
        payment_business_day_convention: Optional[BusinessDayConvention] = None,
        payment_roll_convention: Optional[DateRollingConvention] = None,
        index_reset_frequency: Optional[Frequency] = None,
        index_reset_type: Optional[IndexResetType] = None,
        index_fixing_lag: Optional[int] = None,
        amortization_schedule: Optional[Iterable[AmortizationItem]] = None,
        payment_business_days: Optional[str] = None,
        adjust_interest_to_payment_date: Optional[AdjustInterestToPaymentDate] = None,
        stub_rule: Optional[StubRule] = None,
        barrier_definition: Optional[BarrierDefinitionElement] = None,
        buy_sell: Union[BuySell, str] = None,
        annualized_rebate: Optional[bool] = None,
        cap_digital_payout_percent: Optional[float] = None,
        cap_strike_percent: Optional[float] = None,
        cms_template: Optional[str] = None,
        floor_digital_payout_percent: Optional[float] = None,
        floor_strike_percent: Optional[float] = None,
        index_fixing_ric: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ):
        definition = CapFloorInstrumentDefinition(
            instrument_tag=instrument_tag,
            start_date=start_date,
            end_date=end_date,
            tenor=tenor,
            notional_ccy=notional_ccy,
            notional_amount=notional_amount,
            index_name=index_name,
            index_tenor=index_tenor,
            interest_payment_frequency=interest_payment_frequency,
            interest_calculation_method=interest_calculation_method,
            payment_business_day_convention=payment_business_day_convention,
            payment_roll_convention=payment_roll_convention,
            index_reset_frequency=index_reset_frequency,
            index_reset_type=index_reset_type,
            index_fixing_lag=index_fixing_lag,
            amortization_schedule=amortization_schedule,
            payment_business_days=payment_business_days,
            adjust_interest_to_payment_date=adjust_interest_to_payment_date,
            stub_rule=stub_rule,
            barrier_definition=barrier_definition,
            buy_sell=buy_sell,
            annualized_rebate=annualized_rebate,
            cap_digital_payout_percent=cap_digital_payout_percent,
            cap_strike_percent=cap_strike_percent,
            cms_template=cms_template,
            floor_digital_payout_percent=floor_digital_payout_percent,
            floor_strike_percent=floor_strike_percent,
            index_fixing_ric=index_fixing_ric,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )
