import xml.etree.ElementTree as ET
from collections import namedtuple


class UnexpectedServerMessageType(Exception):
    pass


class MissingResult(Exception):
    pass


class ErrorResponse(Exception):
    pass


class DataManagementError(ErrorResponse):
    pass


class ObjectDoesNotExist(DataManagementError):
    pass


class AuthorizationError(ErrorResponse):
    pass


def get_exc_class(err_code):
    if err_code.startswith('1'):
        return
    elif err_code == '2201':
        return AuthorizationError
    elif err_code == '2303':
        return ObjectDoesNotExist
    else:
        return ErrorResponse


Response = namedtuple('Response', ('code', 'msg', 'data'))


class EPPMapping:
    _epp_ns_url = 'urn:ietf:params:xml:ns:epp-1.0'
    name = ns_url = None

    def __init__(self, transp):
        self._transp = transp

    def _mk_request(self, xml, response_data_extractor):
        self._transp.send(ET.tostring(xml, encoding='UTF8'))
        resp = self._parse_response(self._transp.recv())
        resp = resp._replace(data=response_data_extractor(resp.data))
        return resp

    @classmethod
    def _epp(cls):
        return ET.Element('epp', attrib={
            'xmlns': cls._epp_ns_url,
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation':
                'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'})

    @staticmethod
    def _ns_node(parent, node_tag, ns_name, ns_url):
        se = lambda e, tag, *a, **k: ET.SubElement(
            e, ns_name + ':' + tag, *a, **k)
        n = se(parent, node_tag, attrib={'xmlns:' + ns_name: ns_url})
        return n, se

    @staticmethod
    def _ensure_node(parent, tag, **kw):
        n = parent.find(tag)
        if n is None:
            n = ET.SubElement(parent, tag, **kw)
        return n

    def _cmd_node(self, cmd):
        rootElem = self._epp()
        c = ET.SubElement(rootElem, 'command')
        n = ET.SubElement(c, cmd)
        if self.ns_url:
            n, se = self._ns_node(n, cmd, self.name, self.ns_url)
        else:
            se = ET.SubElement
        return rootElem, n, se

    @staticmethod
    def _ensure_child(parent, tag):
        n = parent.find('.{}'.format(tag))
        if n is None:
            n = ET.SubElement(parent, tag)
        return n

    @staticmethod
    def _get_in_xmlns(ns_url):
        return lambda e, match: e.find('{' + ns_url + '}' + match)

    @staticmethod
    def _get_all_xmlns(ns_url):
        return lambda e, match: e.findall('{' + ns_url + '}' + match)

    def _resData(self, resp):
        se = self._get_in_xmlns(self._epp_ns_url)
        return se(resp, 'resData')

    def _get_extension(self, resp):
        se = self._get_in_xmlns(self._epp_ns_url)
        return se(resp, 'extension')

    def _parse_response(self, xml):
        e = ET.fromstring(xml)
        se = self._get_in_xmlns(self._epp_ns_url)
        resp = se(e, 'response')
        if resp:
            result = se(resp, 'result')
            if result:
                code = result.get('code')
                r = Response(
                    code,
                    se(result, 'msg').text.strip(),
                    resp)
                err_cls = get_exc_class(code)
                if err_cls:
                    raise err_cls(r)
                else:
                    return r
            else:
                raise MissingResult(xml.decode('utf8'))
        else:
            raise UnexpectedServerMessageType(xml.decode('utf8'))

    @staticmethod
    def _add_arc(se, parent, adds, rems, chgs):
        for node_name, items in (('add', adds), ('rem', rems), ('chg', chgs)):
            if items:
                pnode = se(parent, node_name)
                for item in items:
                    item(se, pnode)

    def _update_arc(self, adds, rems, chgs):
        rootElem, d, se = self._cmd_node('update')
        self._add_arc(se, d, adds, rems, chgs)
        return rootElem, d, se


def object_handler(name, ns_url):
    def wrap(cls):
        cls.name = name
        cls.ns_url = ns_url
        return cls
    return wrap


def extract_optional(
        se, xml, d, xml_name, dict_name=None, transform=lambda x: x):
    dict_name = dict_name or xml_name
    node = se(xml, xml_name)
    if node is not None:
        d[dict_name] = transform(node.text)


class Extension:
    @classmethod
    def obj_uri(cls):
        return cls.base.ns_url

    @classmethod
    def wrap(cls, base):
        raise NotImplementedError()
