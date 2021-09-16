# coding: utf8

__all__ = ["MainConstituentAssetClass"]

from enum import Enum, unique

from ..._enums._common_tools import _convert_to_str, _normalize


@unique
class MainConstituentAssetClass(Enum):
    FUTURES = "Futures"
    SWAP = "Swap"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            MainConstituentAssetClass, _MAIN_CONSTITUENT_ASSET_CLASS_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _MAIN_CONSTITUENT_ASSET_CLASS_VALUES_IN_LOWER_BY_MAIN_CONSTITUENT_ASSET_CLASS,
            some,
        )


_MAIN_CONSTITUENT_ASSET_CLASS_VALUES = tuple(t.value for t in MainConstituentAssetClass)
_MAIN_CONSTITUENT_ASSET_CLASS_VALUES_IN_LOWER_BY_MAIN_CONSTITUENT_ASSET_CLASS = {
    name.lower(): item for name, item in MainConstituentAssetClass.__members__.items()
}
