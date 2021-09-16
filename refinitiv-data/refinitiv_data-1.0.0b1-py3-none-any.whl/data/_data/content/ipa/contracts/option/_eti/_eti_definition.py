# coding: utf8

__all__ = ["EtiDefinition"]

from typing import Optional

from .._base import UnderlyingDefinition
from ...instrument._instrument_definition import InstrumentDefinition
from .._enums import (
    BuySell,
    CallPut,
    ExerciseStyle,
    UnderlyingType,
)
from ._eti_barrier_definition import EtiBarrierDefinition
from ._eti_binary_definition import EtiBinaryDefinition
from ._eti_cbbc_definition import EtiCbbcDefinition
from ._eti_double_barriers_definition import EtiDoubleBarriersDefinition
from ._eti_fixing_info import EtiFixingInfo
from ._eti_underlying_definition import EtiUnderlyingDefinition


class EtiDefinition(InstrumentDefinition):
    """
    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    instrument_code : str, optional
        An option RIC that is used to retrieve the description of the
        EtiOptionDefinition contract. Optional.If null, the instrument_code of
        underlying_definition must be provided.
    end_date : str, optional
        Expiry date of the option
    asian_definition : EtiOptionFixingInfo, optional
        Fixing details for asian options
    barrier_definition : EtiOptionBarrierDefinition, optional
        Details for barrier option.
    binary_definition : EtiOptionBinaryDefinition, optional
        Details for binary option.
    buy_sell : BuySell, optional
        The side of the deal. Possible values:
        - Buy
        - Sell
    call_put : CallPut, optional
        Tells if the option is a call or a put. Possible values:
        - Call
        - Put
    cbbc_definition : EtiOptionCbbcDefinition, optional
        Details for CBBC (Call Bear/Bull Contract) option.
    double_barriers_definition : EtiOptionDoubleBarriersDefinition, optional
        Details for double barriers option.
    exercise_style : ExerciseStyle, optional
        EURO or AMER
    underlying_definition : EtiUnderlyingDefinition, optional
        Details of the underlying. Can be used to override some data of the underlying.
    underlying_type : UnderlyingType, optional
        Underlying type of the option. Possible values:
        - Eti
        - Fx
    deal_contract : int, optional
        deal_contract. It is the number of contracts bought or sold in the deal.
    end_date_time : str, optional
        Expiry date time of the option
    lot_size : float, optional
        The lot size. It is the number of options bought or sold in one transaction.
    offset : int, optional
        offset. The offset in minutes between the time UTC and the time of the exchange
        where the contract is traded.
    strike : float, optional
        strike of the option
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        instrument_code: Optional[str] = None,
        end_date: Optional[str] = None,
        asian_definition: Optional[EtiFixingInfo] = None,
        barrier_definition: Optional[EtiBarrierDefinition] = None,
        binary_definition: Optional[EtiBinaryDefinition] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        cbbc_definition: Optional[EtiCbbcDefinition] = None,
        double_barriers_definition: Optional[EtiDoubleBarriersDefinition] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        underlying_definition: Optional[EtiUnderlyingDefinition] = None,
        underlying_type: Optional[UnderlyingType] = None,
        deal_contract: Optional[int] = None,
        end_date_time: Optional[str] = None,
        lot_size: Optional[float] = None,
        offset: Optional[int] = None,
        strike: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(instrument_tag, **kwargs)
        self.instrument_code = instrument_code
        self.end_date = end_date
        self.asian_definition = asian_definition
        self.barrier_definition = barrier_definition
        self.binary_definition = binary_definition
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.cbbc_definition = cbbc_definition
        self.double_barriers_definition = double_barriers_definition
        self.exercise_style = exercise_style
        self.underlying_definition = underlying_definition
        self.underlying_type = underlying_type
        self.deal_contract = deal_contract
        self.end_date_time = end_date_time
        self.lot_size = lot_size
        self.offset = offset
        self.strike = strike

    @property
    def asian_definition(self):
        """
        Fixing details for asian options
        :return: object EtiOptionFixingInfo
        """
        return self._get_object_parameter(EtiFixingInfo, "asianDefinition")

    @asian_definition.setter
    def asian_definition(self, value):
        self._set_object_parameter(EtiFixingInfo, "asianDefinition", value)

    @property
    def barrier_definition(self):
        """
        Details for barrier option.
        :return: object EtiOptionBarrierDefinition
        """
        return self._get_object_parameter(EtiBarrierDefinition, "barrierDefinition")

    @barrier_definition.setter
    def barrier_definition(self, value):
        self._set_object_parameter(EtiBarrierDefinition, "barrierDefinition", value)

    @property
    def binary_definition(self):
        """
        Details for binary option.
        :return: object EtiOptionBinaryDefinition
        """
        return self._get_object_parameter(EtiBinaryDefinition, "binaryDefinition")

    @binary_definition.setter
    def binary_definition(self, value):
        self._set_object_parameter(EtiBinaryDefinition, "binaryDefinition", value)

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
    def cbbc_definition(self):
        """
        Details for CBBC (Call Bear/Bull Contract) option.
        :return: object EtiOptionCbbcDefinition
        """
        return self._get_object_parameter(EtiCbbcDefinition, "cbbcDefinition")

    @cbbc_definition.setter
    def cbbc_definition(self, value):
        self._set_object_parameter(EtiCbbcDefinition, "cbbcDefinition", value)

    @property
    def double_barriers_definition(self):
        """
        Details for double barriers option.
        :return: object EtiOptionDoubleBarriersDefinition
        """
        return self._get_object_parameter(
            EtiDoubleBarriersDefinition, "doubleBarriersDefinition"
        )

    @double_barriers_definition.setter
    def double_barriers_definition(self, value):
        self._set_object_parameter(
            EtiDoubleBarriersDefinition, "doubleBarriersDefinition", value
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
    def underlying_definition(self):
        """
        Details of the underlying. Can be used to override some data of the underlying.
        :return: object EtiUnderlyingDefinition
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
    def deal_contract(self):
        """
        deal_contract. It is the number of contracts bought or sold in the deal.
        :return: int
        """
        return self._get_parameter("dealContract")

    @deal_contract.setter
    def deal_contract(self, value):
        self._set_parameter("dealContract", value)

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
    def end_date_time(self):
        """
        Expiry date time of the option
        :return: str
        """
        return self._get_parameter("endDateTime")

    @end_date_time.setter
    def end_date_time(self, value):
        self._set_parameter("endDateTime", value)

    @property
    def instrument_code(self):
        """
        An option RIC that is used to retrieve the description of the
        EtiOptionDefinition contract. Optional.If null, the instrument_code of
        underlying_definition must be provided.
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def lot_size(self):
        """
        The lot size. It is the number of options bought or sold in one transaction.
        :return: float
        """
        return self._get_parameter("lotSize")

    @lot_size.setter
    def lot_size(self, value):
        self._set_parameter("lotSize", value)

    @property
    def offset(self):
        """
        offset. The offset in minutes between the time UTC and the time of the exchange
        where the contract is traded.
        :return: int
        """
        return self._get_parameter("offset")

    @offset.setter
    def offset(self, value):
        self._set_parameter("offset", value)

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
