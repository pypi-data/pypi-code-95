from random import randrange as _rndrange
from re import sub as _sub


def en_slug(text):
    return _sub(r'[^A-Za-z0-9.-]+', '_', text)


def parse_range(s: str):
    """Parse ranges such as 1,3,6-8,10 to 1,3,6,7,8,10"""
    return _sub(r'(\d+)-(\d+)', _replace_range_part, s)


def human_fmt(num):
    """Format 12500 to 12.5 K"""
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return "%3.1f %s" % (num, unit)
        num /= 1000.0
    return "%.1f %s" % (num, 'Y')


def fmt_bytes(num, suf='B'):
    """Format 1024 to 1 KiB"""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suf)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suf)


def random_lower_alpha():
    return chr(_rndrange(ord('a'), ord('z')))


def random_lower_str(min_len: int = 3, max_len: int = 16):
    return ''.join(random_lower_alpha()
                   for _ in range(_rndrange(min_len, max_len)))



def _replace_range_part(r):
    return ','.join(map(str, range(int(r[1]), int(r[2]))))
