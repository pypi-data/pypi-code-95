import socket
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

from eppzy.connection import connection, LengthPrefixed
from eppzy.rfc5730_epp import EPP


class MissingStuff(Exception):
    pass


class RequestWrapper:
    def __init__(self, wrapee):
        self._wrapee = wrapee

    def __dir__(self):
        return dir(self._wrapee)

    def __getattr__(self, attr):
        f = getattr(self._wrapee, attr)

        @wraps(f)
        def requesting_wrapper(*a, **k):
            xml, response_process = f(*a, **k)
            return self._wrapee._mk_request(xml, response_process)
        return requesting_wrapper


@contextmanager
def _login_and_greet(p, obj_uris, extn_uris, client_id, password):
    e = EPP(p)
    g = e.recv_greeting()
    e = RequestWrapper(e)
    unsupported_objs = obj_uris - g['objUris']
    unsupported_extns = extn_uris - g['extensions']
    if unsupported_objs or unsupported_extns:
        raise MissingStuff('Server did not support {}'.format(
            unsupported_objs | unsupported_extns))
    e.login(obj_uris, extn_uris, client_id, password)
    try:
        yield
    finally:
        e.logout()


@contextmanager
def session(
        objs, extns, host, port, client_id, password, proto=socket.AF_INET,
        proxy_host=None, proxy_port=None):
    obj_extns = defaultdict(list)
    for e in extns:
        obj_extns[e.obj_uri()].append(e)
    obj_uris = {o.ns_url for o in objs}
    if set(obj_extns) - obj_uris:
        raise MissingStuff('Extensions for unrequested objects')
    extn_uris = set()
    for e in extns:
        extn_uris |= e.ext_uris
    with connection(host, port, proto, proxy_host, proxy_port) as c:
        p = LengthPrefixed(c)
        with _login_and_greet(p, obj_uris, extn_uris, client_id, password):
            handled = {}
            for obj in objs:
                cls = obj
                for extn in obj_extns[obj.ns_url]:
                    cls = extn.wrap(cls)
                handled[obj.name] = RequestWrapper(cls(p))
            yield handled
