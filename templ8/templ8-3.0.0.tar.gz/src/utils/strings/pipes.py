def pad_in(string: str, space: int) -> str:
    """
    >>> pad_in('abc', 0)
    'abc'

    >>> pad_in('abc', 2)
    '  abc'
    """
    return "".join([" "] * space) + string


def without_ends(string: str) -> str:
    """
    >>> without_ends('abc')
    'b'
    """
    return string[1:-1]


def without_first(string: str) -> str:
    """
    >>> without_first('abc')
    'bc'
    """
    return string[1:]


def without_last(string: str) -> str:
    """
    >>> without_last('abc')
    'ab'
    """
    return string[:-1]


def quote(string: str) -> str:
    """
    >>> quote('abc')
    '\"abc\"'

    >>> quote('"abc"')
    '\"abc\"'
    """
    return string if string.startswith('"') and string.endswith('"') else f'"{string}"'


def handle(string: str) -> str:
    """
    >>> handle('https://github.com/user/repo')
    'user/repo'

    >>> handle('user/repo')
    'user/repo'

    >>> handle('')
    ''
    """
    splt = string.split("/")
    return "/".join(splt[-2:] if len(splt) >= 2 else splt)


def pluralize(count: int, unit: str) -> str:
    """
    Pluralize a count and given its units.

    >>> pluralize(1, 'file')
    '1 file'

    >>> pluralize(2, 'file')
    '2 files'

    >>> pluralize(0, 'file')
    '0 files'
    """
    return f"{count} {unit}{'s' if count != 1 else ''}"


def remove_prefix(string: str, prefix: str) -> str:
    """
    >>> remove_prefix('abc', 'ab')
    'c'

    >>> remove_prefix('abc', 'd')
    'abc'

    >>> remove_prefix('abc', 'abcd')
    'abc'
    """
    return string[len(prefix) :] if string.startswith(prefix) else string
