# coding: utf8

__all__ = ["OptionInstrumentDefinition"]

from typing import Optional, Union

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
    EtiDefinition,
    EtiCbbcDefinition,
    EtiDoubleBarriersDefinition,
    EtiFixingInfo,
)
from ._fx import (
    FxUnderlyingDefinition,
    FxBinaryDefinition,
    FxBarrierDefinition,
    FxDefinition,
    FxDualCurrencyDefinition,
    FxAverageInfo,
    FxDoubleBarrierDefinition,
    FxDoubleBinaryDefinition,
    FxForwardStart,
)
from ._option_definition import OptionDefinition


class OptionInstrumentDefinition(EtiDefinition, FxDefinition, OptionDefinition):
    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        underlying_type: Optional[UnderlyingType] = None,
        strike: Optional[float] = None,
        tenor: Optional[str] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
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
        asian_definition: Union[EtiFixingInfo, FxAverageInfo] = None,
        cbbc_definition: Optional[EtiCbbcDefinition] = None,
        double_barriers_definition: Optional[EtiDoubleBarriersDefinition] = None,
        deal_contract: Optional[int] = None,
        end_date_time: Optional[str] = None,
        lot_size: Optional[float] = None,
        offset: Optional[int] = None,
    ):
        super().__init__(
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
