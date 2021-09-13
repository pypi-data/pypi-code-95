from html.parser import HTMLParser as _HTMLParser
from pathlib import Path as _Path
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


def to_base(s, b=62):
    s = int(s)
    res = ''
    BS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    while s:
        res += BS[s % b]
        s //= b
    return res[::-1] or '0'


def from_base(s, b=62):
    s = str(s)
    BS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    return sum(b**i * BS.find(c) for i, c in enumerate(s[::-1]))


def is_binary(data: bytes):
    tc = set(range(7, 14)) | {27} | set(range(0x20, 0x100)) - {0x7f}
    return bool(data.translate(None, bytearray(tc)))


def normalize_uri(uri, base):
    from urllib.parse import urlparse, urlunsplit, urljoin
    new = urlparse(urljoin(base, uri).lower())
    return urlunsplit((new.scheme, new.netloc, new.path, new.query, ''))


class ListFile(list):
    """Make list from file"""
    def __init__(self, file_path):
        is_path = isinstance(file_path, _Path)
        with file_path.open() if is_path else open(file_path) as f:
            self.extend(ln.rstrip() for ln in f)


class LinksParser(_HTMLParser):
    def __init__(self):
        super().__init__()
        self.matches = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.matches.append(value)


def _replace_range_part(r):
    return ','.join(map(str, range(int(r[1]), int(r[2]))))
