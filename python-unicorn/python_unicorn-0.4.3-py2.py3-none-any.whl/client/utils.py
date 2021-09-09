# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from requests.adapters import HTTPAdapter


class MyAdapter(HTTPAdapter):
    pass
    #def init_poolmanager(self, connections, maxsize, block=False, **kws):
    #    self.pool


def make_response(r):
    if r.ok:
        return r.json()
    else:
        return {'status': r.ok, 'code': r.status_code, 'text': r.text}
