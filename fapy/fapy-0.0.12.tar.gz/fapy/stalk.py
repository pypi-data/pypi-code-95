from random import randint as _randint
from socket import inet_ntoa as _ntoa
from struct import pack as _pack

from .utils import random_lower_str


def random_path(min_len=8, max_len=12):
    return random_lower_str(min_len, max_len)


def random_wan_ips(count):
    """Get random WAN IP addresses"""
    while count:
        intip = _randint(0x1000000, 0xE0000000)
        if (0xa000000 <= intip <= 0xaffffff
                or 0x64400000 <= intip <= 0x647fffff
                or 0x7f000000 <= intip <= 0x7fffffff
                or 0xa9fe0000 <= intip <= 0xa9feffff
                or 0xac100000 <= intip <= 0xac1fffff
                or 0xc0000000 <= intip <= 0xc0000007
                or 0xc00000aa <= intip <= 0xc00000ab
                or 0xc0000200 <= intip <= 0xc00002ff
                or 0xc0a80000 <= intip <= 0xc0a8ffff
                or 0xc6120000 <= intip <= 0xc613ffff
                or 0xc6336400 <= intip <= 0xc63364ff
                or 0xcb007100 <= intip <= 0xcb0071ff
                or 0xf0000000 <= intip <= 0xffffffff):
            continue
        count -= 1
        yield _ntoa(_pack('>I', intip))
