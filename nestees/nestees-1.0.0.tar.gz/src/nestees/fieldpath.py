'''Helpers for converting field paths to / from strings.'''

import re
from typing import Iterable, Union, Sequence

_BACKSLASH = "\\"
_BACKTICK = "`"
_ESCAPED_BACKSLASH = _BACKSLASH * 2
_ESCAPED_BACKTICK = _BACKSLASH + _BACKTICK

_SIMPLE_FIELD_NAME = re.compile("^[_a-zA-Z][_a-zA-Z0-9]*$")
PATH_ELEMENT_TOKENS = [
    ("SIMPLE", r"[_a-zA-Z]\w*"),     # unquoted elements
    ("QUOTED", r"`(?:\\`|[^`])*?`"), # quoted elements, unquoted
    ("DOT", r"\."),                  # separator
]
TOKENS_PATTERN = "|".join("(?P<{}>{})".format(*pair) for pair in PATH_ELEMENT_TOKENS)
TOKENS_REGEX = re.compile(TOKENS_PATTERN)


def split_field_path(path:  Union[Sequence[str], str]):
    """Split a field path into valid elements (without dots).
    Args:
        path (str): field path to be lexed.
    Returns:
        List(str): tokens
    Raises:
        ValueError: if the path does not match the elements-interspersed-
                    with-dots pattern.
    """
    if not path:
        return []

    if isinstance(path, Sequence) and not isinstance(path, str):
        return path

    elements = []
    want_field = True
    pos = 0    
    match = TOKENS_REGEX.match(path)
    while match is not None:
        match_type = match.lastgroup
        
        if want_field != (match_type != 'DOT'):
            raise ValueError("Invalid path: {}".format(path))
        
        if want_field:
            value = match.group(match_type)
            if match_type == 'QUOTED':
                value = value[1:-1].replace(_ESCAPED_BACKTICK, _BACKTICK)
                value = value.replace(_ESCAPED_BACKSLASH, _BACKSLASH)

            elements.append(value)
        want_field = not want_field
        pos = match.end()
        match = TOKENS_REGEX.match(path, pos)

    if pos != len(path):
        raise ValueError("Path {} not consumed, residue: {}".format(path, path[pos:]))

    return elements


def render_field_path(field_names: Iterable[str]):
    """Create a **field path** from a list of nested field names.

    A **field path** is a ``.``-delimited concatenation of the field
    names. It is used to represent a nested field. For example,
    in the data

    .. code-block: python

       data = {
          'aa': {
              'bb': {
                  'cc': 10,
              },
          },
       }

    the field path ``'aa.bb.cc'`` represents that data stored in
    ``data['aa']['bb']['cc']``.

    Args:
        field_names (Iterable[str, ...]): The list of field names.

    Returns:
        str: The ``.``-delimited field path.
    """
    result = []

    for field_name in field_names:
        match = _SIMPLE_FIELD_NAME.match(field_name)
        if match and match.group(0) == field_name:
            result.append(field_name)
        else:
            replaced = field_name.replace(_BACKSLASH, _ESCAPED_BACKSLASH).replace(
                _BACKTICK, _ESCAPED_BACKTICK
            )
            result.append(_BACKTICK + replaced + _BACKTICK)

    return '.'.join(result)
