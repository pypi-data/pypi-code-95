# coding: utf8

__all__ = ["Direction"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class Direction(Enum):
    """
    The direction of the leg.

    The possible values are:
        Paid - the cash flows of the leg are paid to the counterparty.
        Received - the cash flows of the leg are received from the counterparty.
    """

    PAID = "Paid"
    RECEIVED = "Received"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Direction, _DIRECTION_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DIRECTION_VALUES_IN_LOWER_BY_DIRECTION, some)


_DIRECTION_VALUES = tuple(t.value for t in Direction)
_DIRECTION_VALUES_IN_LOWER_BY_DIRECTION = {
    name.lower(): item for name, item in Direction.__members__.items()
}
