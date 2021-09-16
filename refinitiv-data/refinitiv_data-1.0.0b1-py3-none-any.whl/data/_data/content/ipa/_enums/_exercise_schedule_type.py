# coding: utf8

__all__ = ["ExerciseScheduleType"]

from enum import Enum, unique
from ._common_tools import _convert_to_str, _normalize


@unique
class ExerciseScheduleType(Enum):
    """
    Possible values:
        - FixedLeg
        - FloatLeg
        - UserDefined
    """

    FIXED_LEG = "FixedLeg"
    FLOAT_LEG = "FloatLeg"
    USER_DEFINED = "UserDefined"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            ExerciseScheduleType, _EXERCISE_SCHEDULE_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _EXERCISE_SCHEDULE_TYPE_VALUES_IN_LOWER_BY_EXERCISE_SCHEDULE_TYPE, some
        )


_EXERCISE_SCHEDULE_TYPE_VALUES = tuple(t.value for t in ExerciseScheduleType)
_EXERCISE_SCHEDULE_TYPE_VALUES_IN_LOWER_BY_EXERCISE_SCHEDULE_TYPE = {
    name.lower(): item for name, item in ExerciseScheduleType.__members__.items()
}
