
import sys

import unittest


class Test(unittest.TestCase):

    def test_signer(self):
        from .conf_parser import new_conf
        from .signer import hmac_signer

        conf = new_conf()

        assert conf.hash_strategy in ['hmac-sha1', 'hmac-sha256', 'hmac-sha512']

        assert hmac_signer(message=b'xx', conf=conf) == b's3GZtrZgwIznaq/8u7mlT1QNH8bnSayG1mpQhalN3J0='

    def test_sign(self):
        from .request import HttpRequest
        r = HttpRequest(
            method='post', uri='/v1/userproxy/gw/cmdb/_export/api/jsonrpc/',
            extend_headers={'X-AUTH-USER': 'admin'},
            body={
                "method": "elastic_query_string_dsl",
                "params": {
                    "keyword": "10.10.0"
                },
                "jsonrpc": "2.0",
                "id": 0
            }
        )

        data, code = r.send()
        assert code == 200


    def test_conf(self):
        import os
        os.environ.update({'CMDB_GW_SDK_CONF': '/tmp/conf.ini'})

        from .request import HttpRequest
        r = HttpRequest(
            method='post', uri='/v1/userproxy/gw/cmdb/_export/api/jsonrpc/',
            extend_headers={'X-AUTH-USER': 'admin'},
            body={
                "method": "get_org_struct_tree",
                "params": {
                },
                "jsonrpc": "2.0",
                "id": 0
            }
        )

        data, code = r.send()
        assert code == 200