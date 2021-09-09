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

DEFAULT_BASE_URL = "https://127.0.0.1:5000"
FUNC_KEYS = ('name', 'ename', 'from_field', 'to_field',
             'invoked', 'timestamp', 'author',
             'code', 'description', 'args', 'data_x', 'data_y')


class Client(object):
    """Administration client for Unicorn service.
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
        return "[Admin Client] Unicorn Service on: '{url}'.".format(url=self.url)

    def get(self, name=None, **kws):
        """Get function by *name*.

        Parameters
        ----------
        name : str
            Function name, if not given, return all functions.

        Examples
        --------
        >>> import json
        >>> print(json.dumps(client.get(name='f1')))
        """
        url = self.url
        if name is None:
            r = self._session.get(url,
                                  headers=self.__jsonheader,
                                  verify=False)
        else:
            r = self._session.get('/'.join([url, name]),
                                  headers=self.__jsonheader,
                                  verify=False)
        return make_response(r)

    def create(self, **kws):
        """Create new function.

        Examples
        --------
        >>> code = '''
        >>> def f(x):
        >>>     import numpy
        >>> return numpy.sin(x)**2
        >>> '''
        >>> new_func = {'name': 'f6',
                        'description': 'a new function',
                        'code': code}
        >>> print(client.create(**new_func))
        """
        url = self.url
        data = {k:v for k,v in kws.items() if k in FUNC_KEYS}

        username = kws.get('username', None)
        password = kws.get('password', None)
        if username is None:
            username = r_input("Enter username: ")
        if password is None:
            password = getpass.getpass(
                    "Enter password for '{}': ".format(username))

        r = self._session.post(url, json=data,
                               headers=self.__jsonheader,
                               verify=False,
                               auth=(username, password))
        return make_response(r)

    def update(self, name, **kws):
        """Update function.

        Parameters
        ----------
        name : str
            Name of function.

        Keyword Arguments
        -----------------
        all function fields:
        username : str
            Name of the authorized user.
        password : str
            Password of user.

        Examples
        --------
        >>> code = '''
        >>> def f(x):
        >>>     import numpy
        >>>     return numpy.cos(x)**2
        >>> '''
        >>> new_func = {'name': 'f6',
        >>>             'description': 'a new function',
        >>>             'code': code}
        >>> print(client.update(**new_func))
        """
        url = '/'.join([self.url, name])
        data = {k:v for k,v in kws.items() if k in FUNC_KEYS}

        username = kws.get('username', None)
        password = kws.get('password', None)
        if username is None:
            username = r_input("Enter username: ")
        if password is None:
            password = getpass.getpass(
                    "Enter password for '{}': ".format(username))

        r = self._session.put(url, json=data,
                               headers=self.__jsonheader,
                               verify=False,
                               auth=(username, password))
        return make_response(r)


    def delete(self, name, **kws):
        """Delete function.

        Parameters
        ----------
        name : str
            Name of function.

        Keyword Arguments
        -----------------
        username : str
            Name of the authorized user.
        password : str
            Password of user.

        Examples
        --------
        >>> client.delete('f6')
        """
        url = '/'.join([self.url, name])
        username = kws.get('username', None)
        password = kws.get('password', None)
        if username is None:
            username = r_input("Enter username: ")
        if password is None:
            password = getpass.getpass(
                    "Enter password for '{}': ".format(username))
        r = self._session.delete(url,
                                 verify=False,
                                 auth=(username, password))
        return make_response(r)


if __name__ == "__main__":
    client = Client()
    #print(client)

    client.url = 'http://127.0.0.1:5000'
    #print(client)

    # get
    #import json
    #print(json.dumps(client.get(name='f1')))

    # create
    code = '''
    def f(x):
        import numpy
        return numpy.sin(x)**2
    '''
    new_func = {'name': 'f6',
                'description': 'a new function',
                'code': code}
    print(client.create(**new_func))

    # update
    code = '''
    def f(x):
        import numpy
        return numpy.cos(x)**2
    '''
    new_func = {'name': 'f6',
                'description': 'a new function',
                'code': code}
    print(client.update(**new_func))

    # delete
    #print(client.delete('f6'))
