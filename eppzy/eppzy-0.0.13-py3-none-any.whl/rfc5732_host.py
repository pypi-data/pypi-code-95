from .util import map_partition_rem
from .bases import EPPMapping, object_handler
from .check import check


@object_handler('host', 'urn:ietf:params:xml:ns:host-1.0')
class Host(EPPMapping):
    def check(self, hosts):
        return check(self, hosts)

    def _info_response(self, resp):
        resData = self._resData(resp)
        hse = self._get_in_xmlns(self.ns_url)
        hses = self._get_all_xmlns(self.ns_url)
        i = hse(resData, 'infData')
        v4s = set()
        v6s = set()
        for addr_node in hses(i, 'addr'):
            ipv = addr_node.attrib.get('ip', 'v4')
            if ipv == 'v4':
                v4s.add(addr_node.text)
            elif ipv == 'v6':
                v6s.add(addr_node.text)
            else:
                raise ValueError('Unrecognised IP addr type')
        return {
            'name': hse(i, 'name').text,
            'roid': hse(i, 'roid').text,
            'IPv4': v4s,
            'IPv6': v6s
        }

    def info(self, name):
        rootElem, d, se = self._cmd_node('info')
        se(d, 'name').text = name
        return rootElem, self._info_response

    def _create_response(self, resp):
        resData = self._resData(resp)
        hse = self._get_in_xmlns(self.ns_url)
        creData = hse(resData, 'creData')
        return {
            'name': hse(creData, 'name').text
        }

    def create(self, name, IPv4=(), IPv6=()):
        rootElem, d, se = self._cmd_node('create')
        se(d, 'name').text = name
        for addr in IPv4:
            se(d, 'addr', attrs={'ip': 'v4'}).text = addr
        for addr in IPv6:
            se(d, 'addr', attrs={'ip': 'v6'}).text = addr
        return rootElem, self._create_response

    def delete(self, name):
        rootElem, d, se = self._cmd_node('delete')
        se(d, 'name').text = name
        return rootElem, lambda x: x

    @staticmethod
    def _addr_child(ipv):
        def get_add(ip):
            def add_host(se, d):
                se(d, 'host', attrib={'ip': ipv}).text = ip
            return add_host
        return get_add

    def update(self, name, new_name=None, IPv4=[], IPv6=[]):
        add_v4, rem_v4 = map_partition_rem(self._addr_child('v4'), IPv4)
        add_v6, rem_v6 = map_partition_rem(self._addr_child('v6'), IPv6)
        adds = add_v4 + add_v6
        rems = rem_v4 + rem_v6
        chgs = []
        if new_name is not None:
            @chgs.append
            def chg_name(se, d):
                se(d, 'name').text = str(new_name)
        rootElem, d, se = self._update_arc(adds, rems, chgs)
        se(d, 'name').text = name
        return rootElem, lambda x: x
