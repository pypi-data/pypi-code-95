# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Iterable, Union

from . import PricingParameters
from .._outputs import Outputs
from .._base_definition import BaseDefinition
from ._term_deposit_definition import TermDepositInstrumentDefinition
from ..._enums import BusinessDayConvention, DateRollingConvention, DayCountBasis


class Definition(BaseDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_code : str, optional
        Code to define the term deposit instrument. For the moment, only RICs for CDs
        and Wholesales deposits are supported, with deposit code (ex:"EUR1MD=").
    instrument_tag : str, optional
        User defined string to identify the instrument. It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported.
    start_date : str, optional
        The date the term deposit starts accruing interest. Its effective date.
        By default it is derived from the ValuationDate and the day to spot convention
        of the contract currency.
    end_date : str, optional
        The maturity date of the term deposit contract. Either the endDate or the tenor
        must be provided.
    tenor : str, optional
        The period code that represents the time between the start date and end date of
        the contract.
        Mandatory if instrumentCode is null. Either the endDate or the tenor must be
        provided.
    notional_ccy : str, optional
        The ISO code of the notional currency.
        Should be explicitly specified if InstrumentCode hasn't been specified.
        May be retrieved from reference data.
    notional_amount : float, optional
        The notional amount of the term deposit at the start date.
        By default 1,000,000 is used.
    fixed_rate_percent : float, optional
        Fixed interest rate percent to be applied for notional by deal terms.
        Mandatory if instrument_code is None.
    payment_business_day_convention : BusinessDayConvention, optional
        The method to adjust dates to a working day.
        By default 'ModifiedFollowing'.
    payment_roll_convention : DateRollingConvention, optional
        Method to adjust payment dates when they fall at the end of the month.
        By default 'Last'.
    year_basis : DayCountBasis, optional
        The Day Count Basis method used to calculate the interest payments.
        By default 'Dcb_Actual_365'.
    calendar : str, optional
        Calendar used to adjust deposit duration calculation.
        By default the calendar corresponding to notional currency is used.
    fields : list of str, optional
        Contains the list of Analytics that the quantitative analytic service will
        compute.
    pricing_parameters : PricingParameters, optional
        The pricing parameters to apply to this instrument. If pricing parameters
        are not provided at this level parameters defined globally at the request
        level are used. If no pricing parameters are provided globally default
        values apply.
    outputs : list of str or Outputs, optional
        Contains the sections that will be returned by the API.
    extended_params : dict, optional
        If necessary other parameters.

    Methods
    -------
    get_data(session=session, on_response=on_response, async_mode=None)
        Returns a response to the data platform
    get_data_async(session=session, on_response=on_response, async_mode=None)
        Returns a response to the async data platform
    get_stream(session=session, api="")
        Get stream quantitative analytic service subscription

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> definition = rdf.term_deposit.Definition(
     ...   tenor="5Y",
     ...   notional_ccy="EUR",
     ...   fixed_rate_percent=11
     ...)
     >>> response = definition.get_data()

     Using get_stream
     >>> stream = definition.get_stream()
     >>> stream.open()
    """

    def __init__(
        self,
        instrument_code: Optional[str] = None,
        instrument_tag: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        fixed_rate_percent: Optional[float] = None,
        payment_business_day_convention: Optional[BusinessDayConvention] = None,
        payment_roll_convention: Optional[DateRollingConvention] = None,
        year_basis: Optional[DayCountBasis] = None,
        calendar: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ):
        definition = TermDepositInstrumentDefinition(
            instrument_code=instrument_code,
            instrument_tag=instrument_tag,
            start_date=start_date,
            end_date=end_date,
            tenor=tenor,
            notional_ccy=notional_ccy,
            notional_amount=notional_amount,
            fixed_rate_percent=fixed_rate_percent,
            payment_business_day_convention=payment_business_day_convention,
            payment_roll_convention=payment_roll_convention,
            year_basis=year_basis,
            calendar=calendar,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )

    def __repr__(self):
        from refinitiv.data._data import create_str_definition

        return create_str_definition(
            self,
            middle_path="content.ipa.financial_contracts",
            end_path="term_deposit",
        )
