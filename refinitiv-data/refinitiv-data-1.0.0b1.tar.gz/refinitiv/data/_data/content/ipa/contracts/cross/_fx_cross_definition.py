# coding: utf8

__all__ = ["FxCrossInstrumentDefinition"]

from typing import Optional

from . import LegDefinition
from ._enums import FxCrossType
from ..instrument._instrument_definition import InstrumentDefinition


class FxCrossInstrumentDefinition(InstrumentDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_tag : str, optional
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
    legs : list of LegDefinition, optional
        Extra parameters to describe further the contract. 1 leg is mandatory for
        Forwards and NDFs contracts. 2 legs are required for Swaps, and FwdFwdSwaps
        contracts. Optional for Spot contracts.
    fx_cross_type : FxCrossType, optional
        The type of the Fx Cross instrument :  'FxSpot', 'FxForward',
        'FxNonDeliverableForward', 'FxSwap', 'MultiLeg' or 'FxForwardForward'.
        Mandatory.
    fx_cross_code : str, optional
        The ISO code of the cross currency (e.g. 'EURCHF'). Mandatory.
    ndf_fixing_settlement_ccy : str, optional
        In case of a NDF contract, the ISO code of the settlement currency (e.g. 'EUR'
        ). Optional.
    reference_spot_rate : float, optional
        Contractual Spot Rate the counterparties agreed. It is used to compute the
        traded_cross_rate as 'reference_spot_rate + traded_swap_points /
        FxSwapPointScalingFactor'. In the case of a "FxSwap" contract, it is also used
        to compute  nearLeg.ContraAmount from nearLeg.DealAmount as
        'nearLeg.ContraAmount = nearLeg.DealAmount *  (reference_spot_rate /
        FxCrossScalingFactor)'. Optional. Default value is null. In that case
        traded_cross_rate and Leg ContraAmount may not be computed.
    traded_cross_rate : float, optional
        The contractual exchange rate agreed by the two counterparties.  It is used to
        compute the ContraAmount if the amount is not filled.  In the case of a
        'FxForward' and 'FxNonDeliverableForward' contract : ContraAmount is computed as
        'DealAmount x traded_cross_rate / FxCrossScalingFactor'. In the case of a
        'FxSwap' contract : farLeg.ContraAmount is computed as 'nearLeg.DealAmount x
        traded_cross_rate / FxCrossScalingFactor'. Optional. Default value is null. It
        means that if both ContraAmount and traded_cross_rate are sot set, market value
        cannot be computed.
    traded_swap_points : float, optional
        Contractual forward points agreed by the two counterparties. It is used to
        compute the traded_cross_rate as 'reference_spot_rate + traded_swap_points /
        FxSwapPointScalingFactor'. Optional. Default value is null. In that case
        traded_cross_rate and Leg ContraAmount may not be computed.
    """

    def __init__(
        self,
        *,
        instrument_tag: Optional[str] = None,
        legs: Optional[LegDefinition] = None,
        fx_cross_type: Optional[FxCrossType] = None,
        fx_cross_code: Optional[str] = None,
        ndf_fixing_settlement_ccy: Optional[str] = None,
        reference_spot_rate: Optional[float] = None,
        traded_cross_rate: Optional[float] = None,
        traded_swap_points: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.instrument_tag = instrument_tag
        self.legs = legs
        self.fx_cross_type = fx_cross_type
        self.fx_cross_code = fx_cross_code
        self.ndf_fixing_settlement_ccy = ndf_fixing_settlement_ccy
        self.reference_spot_rate = reference_spot_rate
        self.traded_cross_rate = traded_cross_rate
        self.traded_swap_points = traded_swap_points

    @classmethod
    def get_instrument_type(cls):
        return "FxCross"

    @property
    def fx_cross_type(self):
        """
        The type of the Fx Cross instrument :  'FxSpot', 'FxForward',
        'FxNonDeliverableForward', 'FxSwap', 'MultiLeg' or 'FxForwardForward'.
        Mandatory.
        :return: enum FxCrossType
        """
        return self._get_enum_parameter(FxCrossType, "fxCrossType")

    @fx_cross_type.setter
    def fx_cross_type(self, value):
        self._set_enum_parameter(FxCrossType, "fxCrossType", value)

    @property
    def legs(self):
        """
        Extra parameters to describe further the contract. 1 leg is mandatory for
        Forwards and NDFs contracts. 2 legs are required for Swaps, and FwdFwdSwaps
        contracts. Optional for Spot contracts.
        :return: list LegDefinition
        """
        return self._get_list_parameter(LegDefinition, "legs")

    @legs.setter
    def legs(self, value):
        self._set_list_parameter(LegDefinition, "legs", value)

    @property
    def fx_cross_code(self):
        """
        The ISO code of the cross currency (e.g. 'EURCHF'). Mandatory.
        :return: str
        """
        return self._get_parameter("fxCrossCode")

    @fx_cross_code.setter
    def fx_cross_code(self, value):
        self._set_parameter("fxCrossCode", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output
        results to the instrument definition. Only alphabetic, numeric and '- _.#=@'
        characters are supported. Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def ndf_fixing_settlement_ccy(self):
        """
        In case of a NDF contract, the ISO code of the settlement currency (e.g. 'EUR'
        ). Optional.
        :return: str
        """
        return self._get_parameter("ndfFixingSettlementCcy")

    @ndf_fixing_settlement_ccy.setter
    def ndf_fixing_settlement_ccy(self, value):
        self._set_parameter("ndfFixingSettlementCcy", value)

    @property
    def reference_spot_rate(self):
        """
        Contractual Spot Rate the counterparties agreed. It is used to compute the
        traded_cross_rate as 'reference_spot_rate + traded_swap_points /
        FxSwapPointScalingFactor'. In the case of a "FxSwap" contract, it is also used
        to compute  nearLeg.ContraAmount from nearLeg.DealAmount as
        'nearLeg.ContraAmount = nearLeg.DealAmount *  (reference_spot_rate /
        FxCrossScalingFactor)'. Optional. Default value is null. In that case
        traded_cross_rate and Leg ContraAmount may not be computed.
        :return: float
        """
        return self._get_parameter("referenceSpotRate")

    @reference_spot_rate.setter
    def reference_spot_rate(self, value):
        self._set_parameter("referenceSpotRate", value)

    @property
    def traded_cross_rate(self):
        """
        The contractual exchange rate agreed by the two counterparties.  It is used to
        compute the ContraAmount if the amount is not filled.  In the case of a
        'FxForward' and 'FxNonDeliverableForward' contract : ContraAmount is computed as
        'DealAmount x traded_cross_rate / FxCrossScalingFactor'. In the case of a
        'FxSwap' contract : farLeg.ContraAmount is computed as 'nearLeg.DealAmount x
        traded_cross_rate / FxCrossScalingFactor'. Optional. Default value is null. It
        means that if both ContraAmount and traded_cross_rate are sot set, market value
        cannot be computed.
        :return: float
        """
        return self._get_parameter("tradedCrossRate")

    @traded_cross_rate.setter
    def traded_cross_rate(self, value):
        self._set_parameter("tradedCrossRate", value)

    @property
    def traded_swap_points(self):
        """
        Contractual forward points agreed by the two counterparties. It is used to
        compute the traded_cross_rate as 'reference_spot_rate + traded_swap_points /
        FxSwapPointScalingFactor'. Optional. Default value is null. In that case
        traded_cross_rate and Leg ContraAmount may not be computed.
        :return: float
        """
        return self._get_parameter("tradedSwapPoints")

    @traded_swap_points.setter
    def traded_swap_points(self, value):
        self._set_parameter("tradedSwapPoints", value)
