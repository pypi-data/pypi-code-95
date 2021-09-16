# coding: utf8

__all__ = ["Definition"]

from typing import Optional, Union, Iterable

from ._option_pricing_parameters import PricingParameters
from ._enums import (
    BuySell,
    CallPut,
    ExerciseStyle,
    UnderlyingType,
)
from ._eti import (
    EtiUnderlyingDefinition,
    EtiBinaryDefinition,
    EtiBarrierDefinition,
    EtiCbbcDefinition,
    EtiDoubleBarriersDefinition,
    EtiFixingInfo,
)
from ._fx import (
    FxUnderlyingDefinition,
    FxBinaryDefinition,
    FxBarrierDefinition,
    FxDualCurrencyDefinition,
    FxAverageInfo,
    FxDoubleBarrierDefinition,
    FxDoubleBinaryDefinition,
    FxForwardStart,
)
from ._option_instrument_definition import OptionInstrumentDefinition
from .._base_definition import BaseDefinition
from .._outputs import Outputs


class Definition(BaseDefinition):
    """
    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    end_date : str, optional
        Expiry date of the option
    buy_sell : BuySell, optional
        The side of the deal. Possible values:
        - Buy
        - Sell
    call_put : CallPut, optional
        Tells if the option is a call or a put. Possible values:
        - Call
        - Put
    exercise_style : ExerciseStyle, optional
        EURO or AMER
    underlying_type : UnderlyingType, optional
        Underlying type of the option. Possible values:
        - Eti
        - Fx
    strike : float, optional
        strike of the option
    tenor : str, optional
        tenor of the option
    notional_ccy : str, optional
        Currency of the notional amount If the option is a EURGBP Call option,
        notional_ccy can be expressed in EUR OR GBP
    notional_amount : float, optional
        The notional amount of currency If the option is a EURGBP Call option, amount of
        EUR or GBP of the contract
    asian_definition : FxOptionAverageInfo, EtiOptionFixingInfo, optional
        Fixing details for asian options
    barrier_definition : FxOptionBarrierDefinition, EtiOptionBarrierDefinition, optional
        Details for barrier option.
    binary_definition : FxOptionBinaryDefinition, EtiOptionBinaryDefinition, optional
        Details for binary option.
    double_barrier_definition : FxOptionDoubleBarrierDefinition, optional
        Details for double barriers option.
    double_binary_definition : FxOptionDoubleBinaryDefinition, optional
        Details for double binary option.
    dual_currency_definition : FxDualCurrencyDefinition, optional
        Details for dual currency option.
    forward_start_definition : FxOptionForwardStart, optional
        Details for Forward Start option.
    underlying_definition : FxUnderlyingDefinition, EtiUnderlyingDefinition, optional
        Details of the underlying. Can be used to override some data of the underlying.
    delivery_date : str, optional
        Expiry date of the option
    instrument_code : str, optional
        An option RIC that is used to retrieve the description of the
        EtiOptionDefinition contract. Optional.If null, the instrument_code of
        underlying_definition must be provided.
    cbbc_definition : EtiOptionCbbcDefinition, optional
        Details for CBBC (Call Bear/Bull Contract) option.
    double_barriers_definition : EtiOptionDoubleBarriersDefinition, optional
        Details for double barriers option.
    deal_contract : int, optional
        deal_contract. It is the number of contracts bought or sold in the deal.
    end_date_time : str, optional
        Expiry date time of the option
    lot_size : float, optional
        The lot size. It is the number of options bought or sold in one transaction.
    offset : int, optional
        offset. The offset in minutes between the time UTC and the time of the exchange
        where the contract is traded.
    fields: list of str, optional
        Contains the list of Analytics that the quantitative analytic service will
        compute.
    pricing_parameters : PricingParameters, optional
        The pricing parameters to apply to this instrument. Optional. If pricing
        parameters are not provided at this level parameters defined globally at the
        request level are used. If no pricing parameters are provided globally default
        values apply.
    outputs: list of str, optional
        Contains the sections that will be returned by the API
    extended_params : dict, optional
        If necessary other parameters

    Methods
    -------
    get_data(session=session, on_response=on_response)
        Returns a response to the data platform
    get_stream(session=session, api="")
        Get stream quantitative analytic service subscription

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> definition = rdf.option.Definition(
     ...    instrument_code="FCHI560000L1.p",
     ...    underlying_type=rdf.option.UnderlyingType.ETI,
     ...    outputs=[
     ...        "Data",
     ...        "Headers"
     ...    ],
     ...    fields=[
     ...        "MarketValueInDealCcy",
     ...        "DeltaPercent",
     ...        "GammaPercent",
     ...        "RhoPercent",
     ...        "ThetaPercent",
     ...        "VegaPercent",
     ...        "ErrorCode",
     ...        "ErrorMessage",
     ...    ],
     ... )
     >>> response = definition.get_data()

     Using get_stream
     >>> response = definition.get_stream()
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        underlying_type: Optional[UnderlyingType] = UnderlyingType.ETI,
        strike: Optional[float] = None,
        tenor: Optional[str] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        asian_definition: Union[EtiFixingInfo, FxAverageInfo] = None,
        barrier_definition: Union[FxBarrierDefinition, EtiBarrierDefinition] = None,
        binary_definition: Union[FxBinaryDefinition, EtiBinaryDefinition] = None,
        double_barrier_definition: Optional[FxDoubleBarrierDefinition] = None,
        double_binary_definition: Optional[FxDoubleBinaryDefinition] = None,
        dual_currency_definition: Optional[FxDualCurrencyDefinition] = None,
        forward_start_definition: Optional[FxForwardStart] = None,
        underlying_definition: Union[
            FxUnderlyingDefinition, EtiUnderlyingDefinition
        ] = None,
        delivery_date: Optional[str] = None,
        instrument_code: Optional[str] = None,
        cbbc_definition: Optional[EtiCbbcDefinition] = None,
        double_barriers_definition: Optional[EtiDoubleBarriersDefinition] = None,
        deal_contract: Optional[int] = None,
        end_date_time: Optional[str] = None,
        lot_size: Optional[float] = None,
        offset: Optional[int] = None,
        fields: Optional[Iterable[str]] = None,
        pricing_parameters: Optional[PricingParameters] = None,
        outputs: Union[Iterable[str], Iterable[Outputs]] = None,
        extended_params: Optional[dict] = None,
    ):
        definition = OptionInstrumentDefinition(
            instrument_tag=instrument_tag,
            end_date=end_date,
            buy_sell=buy_sell,
            call_put=call_put,
            exercise_style=exercise_style,
            underlying_type=underlying_type,
            strike=strike,
            tenor=tenor,
            notional_ccy=notional_ccy,
            notional_amount=notional_amount,
            barrier_definition=barrier_definition,
            binary_definition=binary_definition,
            double_barrier_definition=double_barrier_definition,
            double_binary_definition=double_binary_definition,
            dual_currency_definition=dual_currency_definition,
            forward_start_definition=forward_start_definition,
            underlying_definition=underlying_definition,
            delivery_date=delivery_date,
            instrument_code=instrument_code,
            asian_definition=asian_definition,
            cbbc_definition=cbbc_definition,
            double_barriers_definition=double_barriers_definition,
            deal_contract=deal_contract,
            end_date_time=end_date_time,
            lot_size=lot_size,
            offset=offset,
        )
        super().__init__(
            definition=definition,
            fields=fields,
            pricing_parameters=pricing_parameters,
            outputs=outputs,
            extended_params=extended_params,
        )
