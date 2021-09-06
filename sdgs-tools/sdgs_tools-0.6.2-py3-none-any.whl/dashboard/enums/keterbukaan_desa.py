from enum import Enum
from . import make_str_to_enum

MAPPING = {
    "Baik": "1",
    "Cukup": "2",
    "Buruk": "3",
}


class KeterbukaanDesa(Enum):
    BAIK = "1"
    CUKUP = "2"
    BURUK = "3"

    from_str = classmethod(make_str_to_enum(MAPPING))
