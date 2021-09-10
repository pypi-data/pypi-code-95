from collections import namedtuple

from .bases import Extension
from .rfc5731_domain import Domain
from .util import map_partition_rem


DsData = namedtuple('DsData', (
    'key_tag', 'algorithm', 'digest_type', 'digest'))


RemoveAll = object()


class DnsSec(Extension):
    base = Domain
    _dnssec_uri = 'urn:ietf:params:xml:ns:secDNS-1.1'
    ext_uris = {_dnssec_uri}

    @classmethod
    def wrap(cls, base):
        class DnsSecDomain(base):
            def _info_response(self, resp):
                data = super()._info_response(resp)
                ext = self._get_extension(resp)
                se = self._get_in_xmlns(cls._dnssec_uri)
                infData = se(ext, 'infData')
                if infData:
                    ses = self._get_all_xmlns(cls._dnssec_uri)
                    data['dnssec'] = [
                        DsData(
                            int(se(dsData, 'keyTag').text),
                            int(se(dsData, 'alg').text),
                            int(se(dsData, 'digestType').text),
                            se(dsData, 'digest').text
                        ) for dsData in ses(infData, 'dsData')]
                else:
                    data['dnssec'] = []
                return data

            def _extnode(self, x, action):
                ex = self._ensure_child(x[0], 'extension')
                return self._ns_node(ex, action, 'secDNS', cls._dnssec_uri)

            @staticmethod
            def _add_keydata(ds_data):
                def do_add_keydata(se, n):
                    dsd = se(n, 'dsData')
                    se(dsd, 'keyTag').text = str(ds_data.key_tag)
                    se(dsd, 'alg').text = str(ds_data.algorithm)
                    se(dsd, 'digestType').text = str(ds_data.digest_type)
                    se(dsd, 'digest').text = ds_data.digest
                return do_add_keydata

            def create(self, *a, dnssec=[], **k):
                x, pr = super().create(*a, **k)
                if dnssec:
                    n, se = self._extnode(x, 'create')
                    for ds_data in dnssec:
                        self._add_keydata(ds_data)(se, n)
                return x, pr

            @staticmethod
            def _add_rem_all(se, parent):
                se(parent, 'all').text = 'true'

            def update(self, *a, dnssec=[], **k):
                x, pr = super().update(*a, **k)
                if dnssec:
                    n, se = self._extnode(x, 'update')
                    if dnssec is RemoveAll:
                        adds = []
                        rems = [self._add_rem_all]
                    else:
                        adds, rems = map_partition_rem(
                            self._add_keydata, dnssec)
                    self._add_arc(se, n, adds, rems, [])
                return x, pr
        return DnsSecDomain
