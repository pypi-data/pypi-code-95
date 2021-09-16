# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Iterable, Union

from . import PricingParameters
from ._cds_definition import CdsInstrumentDefinition
from ._enums import (
    BusinessDayConvention,
    CdsConvention,
)
from ._models import (
    PremiumLegDefinition,
    ProtectionLegDefinition,
)
from .._base_definition import BaseDefinition
from .._outputs import Outputs


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
    instrument_code : str, optional
        A cds RIC that is used to retrieve the description of the cds contract.
        Optional. If null, the protection_leg and the premium_leg  must be provided.
    cds_convention : CdsConvention, optional
        Define the cds convention. Possible values are:
        - 'ISDA' (start_date will default to accrued_begin_date, end_date will be
          adjusted to IMM Date),
        - 'UserDefined' (start_date will default to step_in_date, end_date will not be
          adjusted). Optional. Defaults to 'ISDA'.
    trade_date : str, optional
        The date the cds contract was created. Optional. By default the valuation date.
    step_in_date : str, optional
        The effective protection date. Optional. By default the trade_date + 1 calendar.
    start_date : str, optional
        The date the cds starts accruing interest. Its effective date. Optional. By
        default it is the accrued_begin_date (the last IMM date before trade_date) if
        cds_convention is ISDA, else it is the step_in_date.
    end_date : str, optional
        The maturity date of the cds contract. Mandatory if instrument_code is null.
        Either the end_date or the tenor must be provided.
    tenor : str, optional
        The period code that represents the time between the start date and end date the
        contract. Mandatory if instrument_code is null. Either the end_date or the tenor
        must be provided.
    start_date_moving_convention : BusinessDayConvention, optional
        The method to adjust the start_date. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
    end_date_moving_convention : BusinessDayConvention, optional
        The method to adjust the end_date.. The possible values are:
        - ModifiedFollowing (adjusts dates according to the Modified Following
          convention - next business day unless is it goes into the next month,
          preceeding is used in that  case),
        - NextBusinessDay (adjusts dates according to the Following convention - Next
          Business Day),
        - PreviousBusinessDay (adjusts dates  according to the Preceeding convention -
          Previous Business Day),
        - NoMoving (does not adjust dates),
        - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following
          convention). Optional. By default 'NoMoving' is used.
    adjust_to_isda_end_date : bool, optional
        The way the end_date is adjusted if computed from tenor input.    The possible
        values are:
        - true ( the end_date is an IMM date computed from start_date according to ISDA
          rules, ),
        - false ( the end_date is computed from start_date according to
          end_dateMovingConvention), Optional. By default true is used if cds_convention
          is ISDA, else false is used.
    protection_leg : ProtectionLegDefinition, optional
        The Protection Leg of the CDS. It is the default leg. Mandatory if instrumenCode
        is null. Optional if instrument_code not null.
    premium_leg : PremiumLegDefinition, optional
        The Premium Leg of the CDS. It is a swap leg paying a fixed coupon. Mandatory if
        instrument_code is null. Optional if instrument_code not null.
    accrued_begin_date : str, optional
        The last cashflow date. Optional. By default it is the last cashflow date.
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
    >>> definition = rdf.cds.Definition(
    ...     instrument_tag="Cds1_InstrumentCode",
    ...     instrument_code="BNPP5YEUAM=R",
    ...     cds_convention=rdf.cds.CdsConvention.ISDA,
    ...     end_date_moving_convention=rdf.cds.BusinessDayConvention.NO_MOVING,
    ...     adjust_to_isda_end_date=True,
    ...     pricing_parameters=rdf.cds.PricingParameters(
    ...         market_data_date="2020-01-01"
    ...     ),
    ...     outputs=["Data", "Headers"],
    ...     fields=[
    ...         "InstrumentTag",
    ...         "ValuationDate",
    ...         "InstrumentDescription",
    ...         "StartDate",
    ...         "EndDate",
    ...         "SettlementDate",
    ...         "UpfrontAmountInDealCcy",
    ...         "CashAmountInDealCcy",
    ...         "AccruedAmountInDealCcy",
    ...         "AccruedBeginDate",
    ...         "NextCouponDate",
    ...         "UpfrontPercent",
    ...         "ConventionalSpreadBp",
    ...         "ParSpreadBp",
    ...         "AccruedDays",
    ...         "ErrorCode",
    ...         "ErrorMessage",
    ...     ],
    ... )
    >>> response = definition.get_data()
    >>> df = response.data.df
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        instrument_code: Optional[str] = None,
        cds_convention: Optional[CdsConvention] = None,
        trade_date: Optional[str] = None,
        step_in_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        start_date_moving_convention: Optional[BusinessDayConvention] = None,
        end_date_moving_convention: Optional[BusinessDayConvention] = None,
        adjust_to_isda_end_date: Optional[bool] = None,
        protection_leg: Optional[ProtectionLegDefinition] = None,
        premium_leg: Optional[PremiumLegDefinition] = None,
        accrued_begin_date: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ):
        definition = CdsInstrumentDefinition(
            cds_convention=cds_convention,
            end_date_moving_convention=end_date_moving_convention,
            premium_leg=premium_leg,
            protection_leg=protection_leg,
            start_date_moving_convention=start_date_moving_convention,
            accrued_begin_date=accrued_begin_date,
            adjust_to_isda_end_date=adjust_to_isda_end_date,
            end_date=end_date,
            instrument_code=instrument_code,
            instrument_tag=instrument_tag,
            start_date=start_date,
            step_in_date=step_in_date,
            tenor=tenor,
            trade_date=trade_date,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )
