from mock import patch
from contextlib import contextmanager
from struct import pack

from eppzy.session import session


class MockTransport:
    def __init__(self, respond, greeting=b''):
        self._respond = respond
        self._set_response(greeting)

    def _set_response(self, b):
        self._response = pack("!i", len(b)) + b

    def send(self, body):
        self._set_response(self._respond(body))

    def recv(self, n_bytes):
        r = self._response[:n_bytes]
        self._response = self._response[n_bytes:]
        return r


@contextmanager
def mock_connection(checks, greeting=b''):
    yield MockTransport(checks, greeting)


@contextmanager
def mocked_session(checks, objs, extns=[]):
    with patch(
            'eppzy.session.connection', return_value=mock_connection(checks)):
        with patch('eppzy.session._login_and_greet'):
            with session(objs, extns, 'ahost', 123, 'clid', 'pwd') as s:
                yield s
