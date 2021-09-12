from random import randint as _randint, shuffle as _shuffle
from socket import SOL_SOCKET, SO_BINDTODEVICE, SO_LINGER, inet_ntoa as _ntoa, socket
from ssl import CERT_REQUIRED, _create_unverified_context as _cuc
from struct import pack as _pack
from time import sleep as _sleep, time as _time

LINGER = _pack('ii', 1, 0)
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def check_addr(addr: tuple, timeout=1, iface: str = None):
    start = _time()

    while _time() - start < 2:
        try:
            with socket() as s:
                s.settimeout(timeout)
                s.setsockopt(SOL_SOCKET, SO_LINGER, LINGER)

                if iface:
                    s.setsockopt(SOL_SOCKET, SO_BINDTODEVICE, iface.encode())

                t = _time()
                res = s.connect_ex(addr) == 0

                return res, _time() - t
        except KeyboardInterrupt:
            raise
        except OSError:
            _sleep(0.5)
        except:
            break


def check_path(host,
               port=80,
               path='/',
               headers=HEADERS,
               ssl=False,
               verify=True):
    if ssl:
        from http.client import HTTPSConnection
        if verify:
            c = HTTPSConnection(host, port)
        else:
            c = HTTPSConnection(host, port, context=_cuc())
    else:
        from http.client import HTTPConnection
        c = HTTPConnection(host, port)

    try:
        c.request('GET', path, headers=headers)
        r = c.getresponse()
        return r.status, r.read()
    except:
        return 999, b''


def domains_from_cert(hostname, port: int = 443, timeout: float = 10):
    from socket import create_connection

    ctx = _cuc(cert_reqs=CERT_REQUIRED)
    addr = (hostname, port)

    try:
        with create_connection(addr, timeout=timeout) as connection:
            with ctx.wrap_socket(connection, server_hostname=hostname) as c:
                ssl_info = c.getpeercert() or {}
                return [v for _, v in ssl_info.get('subjectAltName', [])]
    except:
        pass

    return []


def wan_ip(count):
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


def randomize_ports(ports):
    _shuffle(ports)
    return list(ports)
