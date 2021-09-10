from contextlib import contextmanager
from io import BytesIO
from logging import getLogger
import socket
import ssl
from struct import pack, unpack


_log = getLogger(__name__)


class LengthPrefixed:
    def __init__(self, s):
        self._s = ReadUntilSocket(s)

    def send(self, b):
        _log.debug("sending: %r", b)
        b = pack("!i", len(b)) + b
        self._s.send(b)

    def recv(self):
        _log.debug("receiving")
        r = self._s.read_until(length(4))
        l, = unpack("!i", r)
        _log.debug("expecting %s bytes", l)
        v = self._s.read_until(length(l))
        _log.debug("recieved %r", v)
        return v


class ReadUntilSocket:
    '''A wrapper around a socket that deals reading until a predicate (of
    sorts) matches. Stores any unmatched content to dish out on a regular
    recv() call.
    '''
    recv_size = 1024
    max_size = 1024 ** 2

    def __init__(self, s):
        self._s = s
        self._buf = BytesIO()

    def read_until(self, pred):
        buf = BytesIO()

        while buf.tell() < self.max_size:
            b = self.recv(self.recv_size)
            if b:
                buf.write(b)
                buf_bs = buf.getvalue()
                boundary, drop = pred(buf_bs, len(b))
                if boundary is not None:
                    print('found in', buf_bs, 'at', boundary, 'dropping', drop)
                    self._buf.write(buf_bs[boundary + drop:])
                    return buf_bs[:boundary]
            else:
                raise ValueError('Unexpected end of stream')
        raise ValueError('Read too much without seeing tag')

    def _keep_after(self, n):
        self._buf = BytesIO(self._buf.getvalue()[n:])

    def send(self, b):
        return self._s.send(b)

    def recv(self, n):
        m = self._buf.tell()
        if m:
            b = self._buf.getvalue()[:n]
            self._keep_after(n)
            return b
        else:
            return self._s.recv(n)


def tag(t):
    '''Construct a predicate for read_until() that will read until a given tag
    is present in the stream, and returns the content of the stream up to, but
    not including, the tag.
    '''
    tag_len = len(t)

    def pred(buf_bs, just_read):
        # NB: So that we don't search the same part of the buffer repeatedly:
        start = max(0, len(buf_bs) - just_read - tag_len)
        idx = buf_bs[start:].find(t)
        if idx > 0:
            return start + idx, tag_len
        else:
            return None, None
    return pred


def length(n):
    '''Construct a predicate for read_until() that will read an exact number of
    bytes from the stream
    '''
    def pred(buf_bs, just_read):
        if n <= len(buf_bs):
            return n, 0
        else:
            return None, None
    return pred


def connect(
        host, port, proto=socket.AF_INET, proxy_host=None, proxy_port=None):
    s = socket.socket(proto, socket.SOCK_STREAM)
    s.settimeout(10)
    if proxy_host or proxy_port:
        _log.info(
            'connecting to %s:%s via %s:%s', host, port, proxy_host,
            proxy_port)
        s.connect((proxy_host, proxy_port))
        s = ReadUntilSocket(s)
        s.send(
            'CONNECT {}:{} HTTP/1.1\r\n\r\n'.format(
                host, port
            ).encode('utf-8')
        )
        try:
            r = s.read_until(tag(b'\r\n\r\n'))
        except ValueError as e:
            raise ProxyConnectionError() from e
        if not r.startswith(b'HTTP/1.1 200'):
            raise ProxyConnectionError(r)
    else:
        _log.info('connecting to %s:%s', host, port)
        s.connect((host, port))
    _log.debug('connected to %s:%s', host, port)
    ss = ssl.wrap_socket(s)
    return ss


@contextmanager
def connection(
        host, port, proto=socket.AF_INET, proxy_host=None, proxy_port=None):
    ss = connect(host, port, proto, proxy_host, proxy_port)
    try:
        yield ss
    finally:
        _log.debug('closing connection to %s:%s', host, port)
        ss.close()


class ProxyConnectionError(Exception):
    pass
