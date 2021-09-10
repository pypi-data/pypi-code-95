from enum import Enum, unique
import xml.etree.ElementTree as ET

from .bases import extract_optional, Extension
from .rfc5733_contact import Contact
from .rfc5731_domain import Domain


class NContact(Extension):
    base = Contact
    _contact_nom_uri = 'http://www.nominet.org.uk/epp/xml/contact-nom-ext-1.0'
    ext_uris = {_contact_nom_uri}

    @classmethod
    def wrap(cls, base):
        class NomContact(base):
            def _extend(self, x, ext_subtag, trad_name, type_, co_no):
                ex = self._ensure_child(x[0], 'extension')
                n, se = self._ns_node(
                    ex, ext_subtag, 'ncontact', cls._contact_nom_uri)
                if trad_name is not None:
                    se(n, 'trad-name').text = trad_name
                if type_ is not None:
                    se(n, 'type').text = type_
                if co_no is not None:
                    se(n, 'co-no').text = co_no
                return x

            def create(self, *a, trad_name=None, type_=None, co_no=None, **k):
                x, pr = super().create(*a, **k)
                return self._extend(x, 'create', trad_name, type_, co_no), pr

            def update(self, *a, trad_name=None, type_=None, co_no=None, **k):
                x, pr = super().update(*a, **k)
                return self._extend(x, 'update', trad_name, type_, co_no), pr

            def _info_response(self, resp):
                data = super()._info_response(resp)
                ext = self._get_extension(resp)
                se = self._get_in_xmlns(cls._contact_nom_uri)
                infData = se(ext, 'infData')
                extract_optional(se, infData, data, 'trad-name', 'trad_name')
                extract_optional(se, infData, data, 'type', 'type_')
                extract_optional(se, infData, data, 'co-no', 'co_no')
                return data
        return NomContact


@unique
class RegStatus(Enum):
    REGISTERED = 'Registered until expiry date.'
    NEEDS_RENEWAL = 'Renewal required.'
    NOT_REQUIRED = 'No longer required'

    @classmethod
    def from_msg(cls, msg):
        for e in cls:
            if e.value == msg:
                return e
        raise ValueError(msg)


class NDomain(Extension):
    base = Domain
    _dom_nom_uri = 'http://www.nominet.org.uk/epp/xml/domain-nom-ext-1.2'
    _std_list_uri = 'http://www.nominet.org.uk/epp/xml/std-list-1.0'
    ext_uris = {_dom_nom_uri, _std_list_uri}

    @classmethod
    def wrap(cls, base):
        class NomDomain(base):
            def _extend(
                    self, x, ext_subtag, auto_bill, auto_period,
                    renew_required):
                ex = self._ensure_child(x[0], 'extension')
                n, se = self._ns_node(
                    ex, ext_subtag, 'ndomain', cls._dom_nom_uri)
                if auto_bill is not None:
                    se(n, 'auto-bill').text = str(auto_bill)
                if auto_period is not None:
                    se(n, 'auto-period').text = str(auto_period)
                if renew_required is not None:
                    se(n, 'renew-not-required').text = (
                        'n' if renew_required else 'y')
                return x

            def create(self, *a, auto_bill=None, auto_period=None, **k):
                x, pr = super().create(*a, **k)
                return (
                    self._extend(x, 'create', auto_bill, auto_period, None),
                    pr)

            def update(
                    self, *a, auto_bill=None, auto_period=None,
                    renew_required=None, **k):
                x, pr = super().update(*a, **k)
                return (
                    self._extend(
                        x, 'update', auto_bill, auto_period, renew_required),
                    pr)

            def _info_response(self, resp):
                data = super()._info_response(resp)
                ext = self._get_extension(resp)
                se = self._get_in_xmlns(cls._dom_nom_uri)
                infData = se(ext, 'infData')
                data['status'] = RegStatus.from_msg(
                    se(infData, 'reg-status').text)
                extract_optional(
                    se, infData, data, 'auto-bill', 'auto_bill', int)
                extract_optional(
                    se, infData, data, 'auto-period', 'auto_period', int)
                data['renew_required'] = not se(infData, 'renew-not-required')
                return data

            def _list_response(self, resp):
                resData = self._resData(resp)
                lse = self._get_in_xmlns(cls._std_list_uri)
                lses = self._get_all_xmlns(cls._std_list_uri)
                ld = lse(resData, 'listData')
                return [le.text for le in lses(ld, 'domainName')]

            def list(self, year, month, mode='expiry'):
                rootElem = self._epp()
                c = ET.SubElement(rootElem, 'command')
                n = ET.SubElement(c, 'info')
                l, lse = self._ns_node(n, 'list', 'l', cls._std_list_uri)
                lse(l, mode).text = '{}-{:0=2}'.format(year, month)
                return rootElem, self._list_response
        return NomDomain
