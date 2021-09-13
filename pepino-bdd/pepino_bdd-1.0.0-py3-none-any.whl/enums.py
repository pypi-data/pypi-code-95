from enum import Enum, auto


class Result(Enum):
    NOT_RUN = 1
    PENDING = 2
    RUNNING = 3
    PASSED = 4
    FAILED = 5


class Hook(Enum):

    pre_step = auto()
    post_step = auto()
    pre_background = auto()
    post_background = auto()
    pre_scenario = auto()
    post_scenario = auto()
    pre_feature = auto()
    post_feature = auto()
    pre_rule = auto()
    post_rule = auto()
    call_step = auto()


class Step(Enum):

    WHEN = "when"
    GIVEN = "given"
    THEN = "then"
    AND = "and"
    BUT = "but"
    STAR = "*"
