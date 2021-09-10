from contextlib import contextmanager
import socket

import xml.etree.ElementTree as ET

from .connection import LengthPrefixed, connect
from .rfc5731_domain import Domain
from .rfc5733_contact import Contact
from .session import RequestWrapper


class NominateProto(LengthPrefixed):
    '''Be warned, nominate do a request/response kind of EPP, so a lone recv
    will stall

    Also the requests are 1 per connection'''

    def __init__(self, host, port, proto, proxy_host, proxy_port):
        super().__init__(None)
        self._host = host
        self._port = port
        self._proto = proto
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port

    def send(self, b):
        assert self._s is None
        self._s = connect(
            self._host, self._port, self._proto, self._proxy_host,
            self._proxy_port)
        b = b.replace(b'\n', b'')
        b += b'\n'
        self._s.send(b)

    def recv(self):
        assert self._s is not None
        r = super().recv()
        self._s.close()
        self._s = None
        return r


def nominateify(cls, clid, pw):
    class Nominated(cls):
        def _mk_request(self, xml, response_data_extractor):
            cmd = xml.find('command')
            extn = self._ensure_node(cmd, 'extension')
            loginExt = ET.SubElement(extn, 'client:data')
            ET.SubElement(loginExt, 'id').text = clid
            ET.SubElement(loginExt, 'pw').text = pw
            return super()._mk_request(xml, response_data_extractor)
    return Nominated


class N8Contact(Contact):
    def info(self, roid, domain, contact_type='o'):
        rootElem, c, se = self._cmd_node('info')
        se(c, 'id').text = roid
        cmd = rootElem.find('command')
        extn = self._ensure_node(cmd, 'extension')
        cl = se(extn, 'data')
        ET.SubElement(cl, 'domain').text = domain
        ET.SubElement(cl, 'type').text = contact_type
        return (rootElem, self._info_response)


@contextmanager
def nominate_session(
        host, port, client_id, password, proto=socket.AF_INET, proxy_host=None,
        proxy_port=None):
    proto = NominateProto(host, port, proto, proxy_host, proxy_port)
    n = lambda cls: RequestWrapper(
        nominateify(cls, client_id, password)(proto))
    yield {
        'domain': n(Domain),
        'contact': n(N8Contact)
    }
