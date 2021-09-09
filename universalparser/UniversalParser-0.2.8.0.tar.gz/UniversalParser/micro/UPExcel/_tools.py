import re
from typing import Optional, Tuple

patt = re.compile(r'([A-Z]+)([0-9]+)')

def split_char_number(s: str) -> Optional[Tuple[str, str]]:
    obj = patt.match(s)
    if obj:
        return obj.groups()

def _minus_char(char_begin: str, char_end: str) -> int:
    return ord(char_end) - ord(char_begin) + 1

def _26_to_10(s: str) -> int:
    _26, v = 0, 0
    for _c in s[::-1]:
        v += _minus_char('A', _c) * pow(26, _26)
        _26 += 1
    return v

def get_width_by_char(begin_s: str, end_s: str) -> int:
    return _26_to_10(end_s) - _26_to_10(begin_s) + 1

