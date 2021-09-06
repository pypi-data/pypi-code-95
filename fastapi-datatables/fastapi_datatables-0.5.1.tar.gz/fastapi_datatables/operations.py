from enum import Enum


class FiltrationOperator(Enum):
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THEN = "gt"
    GREATER_THEN_OR_EQUAL = "ge"
    LESS_THEN = "lt"
    LESS_THEN_OR_EQUAL = "le"
    IN = "in"
    NOT_IN = "not_in"
    LIKE = "like"
    ILIKE = "ilike"
    NOT_ILIKE = "not_ilike"
