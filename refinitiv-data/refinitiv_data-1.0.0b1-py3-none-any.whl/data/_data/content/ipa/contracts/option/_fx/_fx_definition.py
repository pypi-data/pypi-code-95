# coding: utf8

__all__ = ["FxDefinition"]

from typing import Optional

from .._base import UnderlyingDefinition
from ...instrument._instrument_definition import InstrumentDefinition
from .._enums import (
    BuySell,
    CallPut,
    ExerciseStyle,
    UnderlyingType,
)
from . import (
    FxDualCurrencyDefinition,
    FxAverageInfo,
    FxBarrierDefinition,
    FxBinaryDefinition,
    FxDoubleBarrierDefinition,
    FxDoubleBinaryDefinition,
    FxForwardStart,
    FxUnderlyingDefinition,
)


class FxDefinition(InstrumentDefinition):
    """
    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    end_date : str, optional
        Expiry date of the option
    tenor : str, optional
        tenor of the option
    notional_ccy : str, optional
        Currency of the notional amount If the option is a EURGBP Call option,
        notional_ccy can be expressed in EUR OR GBP
    notional_amount : float, optional
        The notional amount of currency If the option is a EURGBP Call option, amount of
        EUR or GBP of the contract
    asian_definition : FxOptionAverageInfo, optional
        Fixing details for asian options
    barrier_definition : FxOptionBarrierDefinition, optional
        Details for barrier option.
    binary_definition : FxOptionBinaryDefinition, optional
        Details for binary option.
    buy_sell : BuySell, optional
        The side of the deal. Possible values:
        - Buy
        - Sell
    call_put : CallPut, optional
        Tells if the option is a call or a put. Possible values:
        - Call
        - Put
    double_barrier_definition : FxOptionDoubleBarrierDefinition, optional
        Details for double barriers option.
    double_binary_definition : FxOptionDoubleBinaryDefinition, optional
        Details for double binary option.
    dual_currency_definition : FxDualCurrencyDefinition, optional
        Details for dual currency option.
    exercise_style : ExerciseStyle, optional
        EURO or AMER
    forward_start_definition : FxOptionForwardStart, optional
        Details for Forward Start option.
    underlying_definition : FxUnderlyingDefinition, optional
        The details of the underlying
    underlying_type : UnderlyingType, optional
        Underlying type of the option. Possible values:
        - Eti
        - Fx
    delivery_date : str, optional
        Expiry date of the option
    strike : float, optional
        strike of the option
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        notional_ccy: Optional[str] = None,
        notional_amount: Optional[float] = None,
        asian_definition: Optional[FxAverageInfo] = None,
        barrier_definition: Optional[FxBarrierDefinition] = None,
        binary_definition: Optional[FxBinaryDefinition] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        double_barrier_definition: Optional[FxDoubleBarrierDefinition] = None,
        double_binary_definition: Optional[FxDoubleBinaryDefinition] = None,
        dual_currency_definition: Optional[FxDualCurrencyDefinition] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        forward_start_definition: Optional[FxForwardStart] = None,
        underlying_definition: Optional[FxUnderlyingDefinition] = None,
        underlying_type: Optional[UnderlyingType] = None,
        delivery_date: Optional[str] = None,
        strike: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(instrument_tag, **kwargs)
        self.end_date = end_date
        self.tenor = tenor
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.asian_definition = asian_definition
        self.barrier_definition = barrier_definition
        self.binary_definition = binary_definition
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.double_barrier_definition = double_barrier_definition
        self.double_binary_definition = double_binary_definition
        self.dual_currency_definition = dual_currency_definition
        self.exercise_style = exercise_style
        self.forward_start_definition = forward_start_definition
        self.underlying_definition = underlying_definition
        self.underlying_type = underlying_type
        self.delivery_date = delivery_date
        self.strike = strike

    @property
    def asian_definition(self):
        """
        Fixing details for asian options
        :return: object FxOptionAverageInfo
        """
        return self._get_object_parameter(FxAverageInfo, "asianDefinition")

    @asian_definition.setter
    def asian_definition(self, value):
        self._set_object_parameter(FxAverageInfo, "asianDefinition", value)

    @property
    def barrier_definition(self):
        """
        Details for barrier option.
        :return: object FxOptionBarrierDefinition
        """
        return self._get_object_parameter(FxBarrierDefinition, "barrierDefinition")

    @barrier_definition.setter
    def barrier_definition(self, value):
        self._set_object_parameter(FxBarrierDefinition, "barrierDefinition", value)

    @property
    def binary_definition(self):
        """
        Details for binary option.
        :return: object FxOptionBinaryDefinition
        """
        return self._get_object_parameter(FxBinaryDefinition, "binaryDefinition")

    @binary_definition.setter
    def binary_definition(self, value):
        self._set_object_parameter(FxBinaryDefinition, "binaryDefinition", value)

    @property
    def buy_sell(self):
        """
        The side of the deal. Possible values:
        - Buy
        - Sell
        :return: enum BuySell
        """
        return self._get_enum_parameter(BuySell, "buySell")

    @buy_sell.setter
    def buy_sell(self, value):
        self._set_enum_parameter(BuySell, "buySell", value)

    @property
    def call_put(self):
        """
        Tells if the option is a call or a put. Possible values:
        - Call
        - Put
        :return: enum CallPut
        """
        return self._get_enum_parameter(CallPut, "callPut")

    @call_put.setter
    def call_put(self, value):
        self._set_enum_parameter(CallPut, "callPut", value)

    @property
    def double_barrier_definition(self):
        """
        Details for double barriers option.
        :return: object FxOptionDoubleBarrierDefinition
        """
        return self._get_object_parameter(
            FxDoubleBarrierDefinition, "doubleBarrierDefinition"
        )

    @double_barrier_definition.setter
    def double_barrier_definition(self, value):
        self._set_object_parameter(
            FxDoubleBarrierDefinition, "doubleBarrierDefinition", value
        )

    @property
    def double_binary_definition(self):
        """
        Details for double binary option.
        :return: object FxOptionDoubleBinaryDefinition
        """
        return self._get_object_parameter(
            FxDoubleBinaryDefinition, "doubleBinaryDefinition"
        )

    @double_binary_definition.setter
    def double_binary_definition(self, value):
        self._set_object_parameter(
            FxDoubleBinaryDefinition, "doubleBinaryDefinition", value
        )

    @property
    def dual_currency_definition(self):
        """
        Details for dual currency option.
        :return: object FxDualCurrencyDefinition
        """
        return self._get_object_parameter(
            FxDualCurrencyDefinition, "dualCurrencyDefinition"
        )

    @dual_currency_definition.setter
    def dual_currency_definition(self, value):
        self._set_object_parameter(
            FxDualCurrencyDefinition, "dualCurrencyDefinition", value
        )

    @property
    def exercise_style(self):
        """
        EURO or AMER
        :return: enum ExerciseStyle
        """
        return self._get_enum_parameter(ExerciseStyle, "exerciseStyle")

    @exercise_style.setter
    def exercise_style(self, value):
        self._set_enum_parameter(ExerciseStyle, "exerciseStyle", value)

    @property
    def forward_start_definition(self):
        """
        Details for Forward Start option.
        :return: object FxOptionForwardStart
        """
        return self._get_object_parameter(FxForwardStart, "forwardStartDefinition")

    @forward_start_definition.setter
    def forward_start_definition(self, value):
        self._set_object_parameter(FxForwardStart, "forwardStartDefinition", value)

    @property
    def underlying_definition(self):
        """
        The details of the underlying
        :return: object FxUnderlyingDefinition
        """
        return self._get_object_parameter(UnderlyingDefinition, "underlyingDefinition")

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(UnderlyingDefinition, "underlyingDefinition", value)

    @property
    def underlying_type(self):
        """
        Underlying type of the option. Possible values:
        - Eti
        - Fx
        :return: enum UnderlyingType
        """
        return self._get_enum_parameter(UnderlyingType, "underlyingType")

    @underlying_type.setter
    def underlying_type(self, value):
        self._set_enum_parameter(UnderlyingType, "underlyingType", value)

    @property
    def delivery_date(self):
        """
        Expiry date of the option
        :return: str
        """
        return self._get_parameter("deliveryDate")

    @delivery_date.setter
    def delivery_date(self, value):
        self._set_parameter("deliveryDate", value)

    @property
    def end_date(self):
        """
        Expiry date of the option
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def notional_amount(self):
        """
        The notional amount of currency If the option is a EURGBP Call option, amount of
        EUR or GBP of the contract
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def notional_ccy(self):
        """
        Cuurency of the notional amount If the option is a EURGBP Call option,
        notional_ccy can be expressed in EUR OR GBP
        :return: str
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        self._set_parameter("notionalCcy", value)

    @property
    def strike(self):
        """
        strike of the option
        :return: float
        """
        return self._get_parameter("strike")

    @strike.setter
    def strike(self, value):
        self._set_parameter("strike", value)

    @property
    def tenor(self):
        """
        tenor of the option
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)
