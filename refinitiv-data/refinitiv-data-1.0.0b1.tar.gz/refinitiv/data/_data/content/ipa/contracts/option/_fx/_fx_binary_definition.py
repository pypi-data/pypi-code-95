# coding: utf8

__all__ = ["FxBinaryDefinition"]

from typing import Optional

from .._base import BinaryDefinition
from .._enums import (
    FxBinaryType,
    SettlementType,
)


class FxBinaryDefinition(BinaryDefinition):
    """
    Parameters
    ----------
    binary_type : FxBinaryType, optional
        Binary Type of the digital option
    settlement_type : SettlementType, optional
        Settlement Type of the BinaryOption
    payout_amount : float, optional
        Payout of the binary option. Default
    payout_ccy : str, optional
        Payout Currency of the binary option. Default
    trigger : float, optional
        trigger of the binary option.
    """

    def __init__(
        self,
        binary_type: Optional[FxBinaryType] = None,
        settlement_type: Optional[SettlementType] = None,
        payout_amount: Optional[float] = None,
        payout_ccy: Optional[str] = None,
        trigger: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.binary_type = binary_type
        self.settlement_type = settlement_type
        self.payout_amount = payout_amount
        self.payout_ccy = payout_ccy
        self.trigger = trigger

    @property
    def binary_type(self):
        """
        Binary Type of the digital option
        :return: enum FxBinaryType
        """
        return self._get_enum_parameter(FxBinaryType, "binaryType")

    @binary_type.setter
    def binary_type(self, value):
        self._set_enum_parameter(FxBinaryType, "binaryType", value)

    @property
    def settlement_type(self):
        """
        Settlement Type of the BinaryOption
        :return: enum SettlementType
        """
        return self._get_enum_parameter(SettlementType, "settlementType")

    @settlement_type.setter
    def settlement_type(self, value):
        self._set_enum_parameter(SettlementType, "settlementType", value)

    @property
    def payout_amount(self):
        """
        Payout of the binary option. Default
        :return: float
        """
        return self._get_parameter("payoutAmount")

    @payout_amount.setter
    def payout_amount(self, value):
        self._set_parameter("payoutAmount", value)

    @property
    def payout_ccy(self):
        """
        Payout Currency of the binary option. Default
        :return: str
        """
        return self._get_parameter("payoutCcy")

    @payout_ccy.setter
    def payout_ccy(self, value):
        self._set_parameter("payoutCcy", value)

    @property
    def trigger(self):
        """
        trigger of the binary option.
        :return: float
        """
        return self._get_parameter("trigger")

    @trigger.setter
    def trigger(self, value):
        self._set_parameter("trigger", value)
