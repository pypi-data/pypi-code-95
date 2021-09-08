from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

__all__ = ['PrepType']


class PrepType(Enum):
    """
    Column type for Tableau Prep.
    """

    BOOL = 'prep_bool_type'
    DATE = 'prep_date_type'
    DATETIME = 'prep_datetime_type'
    DECIMAL = 'prep_decimal_type'
    INT = 'prep_int_type'
    STR = 'prep_string_type'


def __dir__() -> 'List[str]':
    return __all__
