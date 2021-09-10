from .util import parse_datetime, map_partition_rem, map_partition_rem_dict
from eppzy.bases import EPPMapping, object_handler, extract_optional
from eppzy.check import check


@object_handler('domain', 'urn:ietf:params:xml:ns:domain-1.0')
class Domain(EPPMapping):
    def _info_response(self, resp):
        resData = self._resData(resp)
        dse = self._get_in_xmlns(self.ns_url)
        dses = self._get_all_xmlns(self.ns_url)
        i = dse(resData, 'infData')
        mns = dse(i, 'ns')
        ns = [n.text for n in dses(mns, 'hostObj')] if mns else []
        data = {
            'name': dse(i, 'name').text,
            'roid': dse(i, 'roid').text,
            'host': [n.text for n in dses(i, 'host')],
            'ns': ns
        }
        extract_optional(dse, i, data, 'registrant')
        extract_optional(dse, i, data, 'crDate')
        extract_optional(dse, i, data, 'exDate')
        return data

    def info(self, name, domain_pw=''):
        rootElem, d, se = self._cmd_node('info')
        se(d, 'name', attrib={'hosts': 'all'}).text = name
        ai = se(d, 'authInfo')
        se(ai, 'pw').text = domain_pw
        return (rootElem, self._info_response)

    def check(self, names):
        return check(self, names)

    def _create_response(self, resp):
        resData = self._resData(resp)
        dse = self._get_in_xmlns(self.ns_url)
        creData = dse(resData, 'creData')
        data = {
            'name': dse(creData, 'name').text,
            'created_date': parse_datetime(dse(creData, 'crDate').text)}
        extract_optional(
            dse, creData, data, 'exDate', dict_name='expiry_date',
            transform=parse_datetime)
        return data

    @staticmethod
    def _ns_child(ns):
        def add_ns(se, d):
            nn = se(d, 'ns')
            se(nn, 'hostObj').text = ns
        return add_ns

    @staticmethod
    def _contact_child(ctype, c):
        def add_contact(se, d):
            se(d, 'contact', attrs={'type': ctype}).text = c
        return add_contact

    def create(
            self, name, *, period=None, period_unit='y', ns=[],
            registrant=None, contacts={}, password=None):
        rootElem, d, se = self._cmd_node('create')
        se(d, 'name').text = name
        if period:
            se(d, 'period', attrs={'unit': period_unit}).text = period
        if ns:
            for n in ns:
                self._ns_child(n)(se, d)
        if registrant:
            se(d, 'registrant').text = registrant
        if contacts:
            for ctype, c in contacts.items():
                self._contact_child(ctype, c)(se, d)
        authInfo = se(d, 'authInfo')
        if password:
            se(authInfo, 'pw').text = password
        return (rootElem, self._create_response)

    def delete(self, name):
        rootElem, d, se = self._cmd_node('delete')
        se(d, 'name').text = name
        return rootElem, lambda x: x

    def _renew_response(self, resp):
        resData = self._resData(resp)
        dse = self._get_in_xmlns(self.ns_url)
        renData = dse(resData, 'renData')
        data = {'name': dse(renData, 'name').text}
        extract_optional(
            dse, renData, data, 'exDate', dict_name='new_expiry_date',
            transform=parse_datetime)
        return data

    def renew(
            self, name, current_expiry_date, *, period=None,
            period_unit='y'):
        rootElem, d, se = self._cmd_node('renew')
        se(d, 'name').text = name
        se(d, 'curExpDate').text = str(current_expiry_date)
        if period:
            se(d, 'period', attrib={'unit', period_unit}).text = period
        return rootElem, self._renew_response

    @staticmethod
    def _status_child(status, msg):
        def add_status(se, d):
            se(d, 'status', attrib={'s': status, 'lang': 'en'}).text = msg
        return add_status

    def update(
            self, name, ns=[], contacts={}, status={}, registrant=None):
        add_ns, rem_ns = map_partition_rem(self._ns_child, ns)
        add_contact, rem_contact = map_partition_rem_dict(
            self._contact_child, contacts)
        add_status, rem_status = map_partition_rem_dict(
            self._status_child, status)
        adds = add_ns + add_contact + add_status
        rems = rem_ns + rem_contact + rem_status
        chgs = []
        if registrant is not None:
            @chgs.append
            def add_registrant(se, d):
                se(d, 'registrant').text = str(registrant)
        rootElem, d, se = self._update_arc(adds, rems, chgs)
        se(d, 'name').text = name
        return rootElem, lambda x: x
