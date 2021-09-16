# coding: utf8

__all__ = ["OptionDefinition"]

from typing import Optional

from ..instrument._instrument_definition import InstrumentDefinition
from ._enums import (
    BuySell,
    CallPut,
    ExerciseStyle,
    UnderlyingType,
)


class OptionDefinition(InstrumentDefinition):
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
    """

    def __init__(
        self,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        underlying_type: Optional[UnderlyingType] = None,
        strike: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(instrument_tag, **kwargs)
        self.end_date = end_date
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.exercise_style = exercise_style
        self.underlying_type = underlying_type
        self.strike = strike

    @classmethod
    def get_instrument_type(cls):
        return "Option"

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
    def strike(self):
        """
        strike of the option
        :return: float
        """
        return self._get_parameter("strike")

    @strike.setter
    def strike(self, value):
        self._set_parameter("strike", value)
