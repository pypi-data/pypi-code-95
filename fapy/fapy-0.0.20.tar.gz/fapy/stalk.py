from random import randint as _randint
from re import findall as _findall
from socket import inet_ntoa as _ntoa
from struct import pack as _pack

from fapy.net import check_path as _chp

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


def _result_filter(r):
    return bool(r[0]) if isinstance(r, tuple) else bool(r)


def netrandom(check_fn,
              result_fn=print,
              filter_fn=_result_filter,
              limit=1000000,
              workers=512,
              start_cb=lambda: None,
              stop_cb=lambda: None):
    from threading import Thread, Event, Lock
    import sys

    threads = []
    running = Event()
    gen_lock = Lock()
    print_lock = Lock()
    generator = random_wan_ips(limit)
    results = []

    def wrapped():
        while running.is_set():
            try:
                with gen_lock:
                    ip = next(generator)
            except StopIteration:
                break

            res = check_fn(ip)
            if filter_fn(res):
                with print_lock:
                    results.append((ip, res))
                    result_fn(ip, res)

    for _ in range(workers):
        t = Thread(target=wrapped)
        threads.append(t)

    running.set()

    start_cb()

    try:
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        running.clear()
        sys.stderr.write('\rStopping...\n')

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        sys.stderr.write('\rKilled\n')

    stop_cb()
    return results


def check_spa(host, port=80, ssl=False, timeout=2):
    path = random_path()
    code, _ = _chp(host, port, path, ssl=ssl, verify=False, timeout=timeout)
    return 200 <= code < 300


def path_checker(path, port=80, ssl=False, timeout=2, body_re=''):
    def f(host):
        _path = random_path()

        code, _ = _chp(host, port, _path, ssl=ssl, timeout=timeout)

        if not 200 <= code < 300 and code != 999:
            code, body = _chp(host, port, path, ssl=ssl, timeout=timeout)
            if body_re and _findall(body_re, body.decode(errors='ignore')):
                return 200 <= code < 300, body

        return False, b''

    return f
