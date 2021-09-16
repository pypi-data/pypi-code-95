# coding: utf8

__all__ = ["SettlementType"]

from enum import Enum, unique

from refinitiv.data._data.content.ipa._enums._common_tools import (
    _convert_to_str,
    _normalize,
)


@unique
class SettlementType(Enum):
    ASSET = "Asset"
    CASH = "Cash"
    UNDEFINED = "Undefined"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(SettlementType, _SETTLEMENT_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SETTLEMENT_TYPE, some)


_SETTLEMENT_TYPE_VALUES = tuple(t.value for t in SettlementType)
_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SETTLEMENT_TYPE = {
    name.lower(): item for name, item in SettlementType.__members__.items()
}
