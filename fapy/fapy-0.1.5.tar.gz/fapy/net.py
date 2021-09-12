from http.client import HTTPConnection, HTTPSConnection
from random import shuffle as _shuffle
from socket import (
    SOL_SOCKET,
    SOL_TCP,
    SO_BINDTODEVICE,
    SO_LINGER,
    TCP_NODELAY,
    gethostbyaddr as _gethostbyaddr,
    socket,
)
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
                s.setsockopt(SOL_TCP, TCP_NODELAY, True)

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


def http_connection(host: str, port=80, ssl=False, verify=False, timeout=2):
    if ssl:
        return (HTTPSConnection(host, port, timeout=timeout) if verify else
                HTTPSConnection(host, port, context=_cuc(), timeout=timeout))

    else:
        return HTTPConnection(host, port, timeout=timeout)


def http_request(connection: HTTPConnection, path, headers: dict = HEADERS):
    try:
        connection.request('GET', path, headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    except KeyboardInterrupt:
        raise
    except:
        return 999, b''


def check_path(host, port=80, path='/', headers=HEADERS, ssl=False, timeout=2):
    c = http_connection(host, port, ssl, False, timeout)
    res = http_request(c, path, headers)
    c.close()
    return res


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


def randomize_ports(ports):
    _shuffle(ports)
    return list(ports)


def reverse_dns(ip):
    try:
        return _gethostbyaddr(ip)[0]
    except:
        return
