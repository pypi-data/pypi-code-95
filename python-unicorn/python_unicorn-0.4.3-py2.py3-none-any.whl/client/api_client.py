# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import requests
import getpass

from .utils import MyAdapter
from .utils import make_response

try:
    r_input = raw_input
except NameError:
    r_input = input

DEFAULT_BASE_URL = "https://127.0.0.1:5000/api/v1.0"
FUNC_KEYS = ('name', 'invoked', 'timestamp', 'author',
             'udef', 'description', 'args')


class Client(object):
    """Function evaluation API client for Unicorn service.
    """
    __jsonheader = {'content-type': 'application/json'}

    def __init__(self, base_url=None):
        self._url_config = [DEFAULT_BASE_URL, '/functions']
        self.url = base_url
        self._session = requests.Session()
        self._session.mount(self.url, MyAdapter())
    
    @property
    def url(self):
        """Base URL.
        """
        return ''.join(self._url_config)

    @url.setter
    def url(self, u):
        if u is None:
            self._url_config[0] = DEFAULT_BASE_URL
        else:
            self._url_config[0] = u

    def __repr__(self):
        return "[Function API] Unicorn Service on: '{url}'.".format(url=self.url)


    def get(self, name, **kws):
        """Get evaluation result from function defined by *name*, key-value
        pairs as function's input parameters.
        """
        url = '/'.join([self.url, name])
        r = self._session.get(url, params=kws, verify=False)
        return make_response(r)


if __name__ == "__main__":
    client = Client()

    print(client.get('f1', x=1, y=2))
