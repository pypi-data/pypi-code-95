# coding: utf8

__all__ = ["CallPut"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class CallPut(Enum):
    """
    Tells if the option is a call or a put.

    Possible values:
        - Call
        - Put
        - None
    """

    CALL = "CALL"
    NONE = "None"
    PUT = "PUT"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CallPut, _CALL_PUT_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_CALL_PUT_VALUES_IN_LOWER_BY_CALL_PUT, some)


_CALL_PUT_VALUES = tuple(t.value for t in CallPut)
_CALL_PUT_VALUES_IN_LOWER_BY_CALL_PUT = {
    name.lower(): item for name, item in CallPut.__members__.items()
}
