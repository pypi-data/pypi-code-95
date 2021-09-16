# coding: utf8

__all__ = ["FxBinaryType"]

from enum import Enum, unique
from refinitiv.data._data.content.ipa._enums._common_tools import (
    _convert_to_str,
    _normalize,
)


@unique
class FxBinaryType(Enum):
    DIGITAL = "Digital"
    NO_TOUCH = "NoTouch"
    NONE = "None"
    ONE_TOUCH_DEFERRED = "OneTouchDeferred"
    ONE_TOUCH_IMMEDIATE = "OneTouchImmediate"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FxBinaryType, _FX_BINARY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FX_BINARY_TYPE_VALUES_IN_LOWER_BY_FX_BINARY_TYPE, some)


_FX_BINARY_TYPE_VALUES = tuple(t.value for t in FxBinaryType)
_FX_BINARY_TYPE_VALUES_IN_LOWER_BY_FX_BINARY_TYPE = {
    name.lower(): item for name, item in FxBinaryType.__members__.items()
}
