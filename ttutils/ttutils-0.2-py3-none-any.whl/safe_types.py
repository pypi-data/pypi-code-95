import html
from typing import Any, List, Optional, Iterable, Set


def try_int(value: Any) -> Optional[int]:
    """ Convert any value to int or None (if impossible) """
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def as_bool(value: Any) -> bool:
    """ Return True if value like true """
    return value in (True, 1, '1', 'True', 'true', 't', b'1', b'True', b'true', b't')


def to_string(val: Any) -> str:
    """ Convert value to string """
    if isinstance(val, bytes):
        return str(val, 'utf8', 'strict')

    if not isinstance(val, str):
        return str(val)

    return val


def safe_text(text: str) -> str:
    """ Escape tags from text """
    return html.escape(text, True).replace('\xa0', ' ') if text else text


def text_crop(text: str, length: int) -> str:
    """ Crop text """
    if len(text) > length:
        return text[:length - 2] + ' …'

    return text


def int_list(values: Iterable[Any]) -> List[int]:
    """ Take list of any values and return list of integer where value is convertible """
    return list(filter(None, map(try_int, values)))


def int_set(values: Iterable[Any]) -> Set[int]:
    """ Like int_list but return set """
    return set(int_list(values))
