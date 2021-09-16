# coding: utf8
from typing import Optional

from refinitiv.data._data.content.ipa.contracts import swap
from . import BermudanSwaptionDefinition
from ..instrument._instrument_definition import InstrumentDefinition
from ..swap._swap_definition import SwapInstrumentDefinition
from ._enums import BuySell
from ._enums import CallPut
from ._enums import ExerciseStyle
from ._enums import SwaptionSettlementType


class SwaptionInstrumentDefinition(InstrumentDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported.
    end_date : str, optional
        Expiry date of the option.
    tenor : str, optional
        Tenor of the option.
    notional_amount : float, optional
        The notional amount of the underlying swap.
        By default 1,000,000 is used.
    bermudan_swaption_definition : BermudanSwaptionDefinition, optional

    buy_sell : BuySell
        The direction of the trade in terms of the deal currency : 'Buy' or 'Sell'.
    call_put : CallPut
        Tells if the option is a call or a put.
    exercise_style : ExerciseStyle, optional
        EURO or BERM or AMER.
    settlement_type : SwaptionSettlementType, optional
        The settlement type of the option if the option is exercised.
    underlying_definition : swap.Definition, optional
        The details of the underlying swap.
    spread_vs_atm_in_bp : float, optional
        Spread between strike and atm strike, expressed in basis points (bp).
    strike_percent : float, optional
        strike_percent of the option expressed in % format.
    """

    def __init__(
        self,
        *,
        instrument_tag: Optional[str] = None,
        end_date: Optional[str] = None,
        tenor: Optional[str] = None,
        notional_amount: Optional[float] = None,
        bermudan_swaption_definition: Optional[BermudanSwaptionDefinition] = None,
        buy_sell: Optional[BuySell] = None,
        call_put: Optional[CallPut] = None,
        exercise_style: Optional[ExerciseStyle] = None,
        settlement_type: Optional[SwaptionSettlementType] = None,
        underlying_definition: Optional[swap.Definition] = None,
        spread_vs_atm_in_bp: Optional[float] = None,
        strike_percent: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.instrument_tag = instrument_tag
        self.end_date = end_date
        self.tenor = tenor
        self.notional_amount = notional_amount
        self.bermudan_swaption_definition = bermudan_swaption_definition
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.exercise_style = exercise_style
        self.settlement_type = settlement_type
        self.underlying_definition = underlying_definition
        self.spread_vs_atm_in_bp = spread_vs_atm_in_bp
        self.strike_percent = strike_percent

    @classmethod
    def get_instrument_type(cls):
        return "Swaption"

    @property
    def bermudan_swaption_definition(self):
        """
        :return: object BermudanSwaptionDefinition
        """
        return self._get_object_parameter(
            BermudanSwaptionDefinition, "bermudanSwaptionDefinition"
        )

    @bermudan_swaption_definition.setter
    def bermudan_swaption_definition(self, value):
        self._set_object_parameter(
            BermudanSwaptionDefinition, "bermudanSwaptionDefinition", value
        )

    @property
    def buy_sell(self):
        """
        The side of the deal.
        :return: enum BuySell
        """
        return self._get_enum_parameter(BuySell, "buySell")

    @buy_sell.setter
    def buy_sell(self, value):
        self._set_enum_parameter(BuySell, "buySell", value)

    @property
    def call_put(self):
        """
        Tells if the option is a call or a put.
        :return: enum CallPut
        """
        return self._get_enum_parameter(CallPut, "callPut")

    @call_put.setter
    def call_put(self, value):
        self._set_enum_parameter(CallPut, "callPut", value)

    @property
    def exercise_style(self):
        """
        :return: enum ExerciseStyle
        """
        return self._get_enum_parameter(ExerciseStyle, "exerciseStyle")

    @exercise_style.setter
    def exercise_style(self, value):
        self._set_enum_parameter(ExerciseStyle, "exerciseStyle", value)

    @property
    def settlement_type(self):
        """
        The settlement type of the option if the option is exercised.
        :return: enum SwaptionSettlementType
        """
        return self._get_enum_parameter(SwaptionSettlementType, "settlementType")

    @settlement_type.setter
    def settlement_type(self, value):
        self._set_enum_parameter(SwaptionSettlementType, "settlementType", value)

    @property
    def underlying_definition(self):
        """
        The details of the underlying swap.
        :return: object SwapDefinition
        """
        return self._get_object_parameter(
            SwapInstrumentDefinition, "underlyingDefinition"
        )

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(
            SwapInstrumentDefinition, "underlyingDefinition", value
        )

    @property
    def end_date(self):
        """
        Expiry date of the option.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output results to the instrument definition.
        Only alphabetic, numeric and '- _.#=@' characters are supported.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def strike_percent(self):
        """
        StrikePercent of the option expressed in % format.
        :return: float
        """
        return self._get_parameter("strikePercent")

    @strike_percent.setter
    def strike_percent(self, value):
        self._set_parameter("strikePercent", value)

    @property
    def tenor(self):
        """
        Tenor of the option.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def notional_amount(self):
        """
        The notional amount of the underlying swap.
        By default 1,000,000 is used.
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def spread_vs_atm_in_bp(self):
        """
        Spread between strike and atm strike, expressed in basis points (bp).
        :return: float
        """
        return self._get_parameter("spreadVsAtmInBp")

    @spread_vs_atm_in_bp.setter
    def spread_vs_atm_in_bp(self, value):
        self._set_parameter("spreadVsAtmInBp", value)
