import json
import os
import pickle
import logging
from urllib.parse import urljoin, urlparse, parse_qsl

import requests
from requests import Session
from requests.utils import dict_from_cookiejar, cookiejar_from_dict
from requests_toolbelt import user_agent

from moosetools import __app__, __version__

"""default logger"""
logger = logging.getLogger(__name__)

"""default directory to store cookies and other cache"""
_default_store_: os.path = os.getcwd()
_default_cookies_ext_: str = '.cookies'

"""user-agent for connection"""
_user_agent_header: dict = {'User-Agent': user_agent(__app__, __version__)}


class AppSession(Session):
    """A Session with a URL that all requests will use as a base.
    Let's start by looking at an example:

    original code came from requests_toolbelt: https://github.com/requests/toolbelt/blob/master/requests_toolbelt/sessions.py
    """

    base_url: str = None
    app: str = __name__
    store: os.path = os.getcwd()
    session_keys: list = []

    def __init__(self, base_url: str, app: str, store: os.path = None, *args, **kwargs):
        if base_url:
            if not base_url.endswith('/'):
                base_url = f'{base_url}/'
            self.base_url = base_url

        if app:
            self.app = app

        if store is not None:
            self.store = store

        super(AppSession, self).__init__(**kwargs)

        self.reload_session()

    def request(self, method, url, *args, **kwargs):
        """Send the request after generating the complete URL."""
        url = self.create_url(url)
        return super(AppSession, self).request(method, url, *args, **kwargs)

    def create_url(self, url):
        """Create the URL based off this partial path."""
        return urljoin(self.base_url, url.lstrip('/'))

    @property
    def session_store(self) -> str:
        """store location for sessions"""
        return os.path.join(self.store, f'.{self.app}.session')

    @property
    def unique_session_keys(self):
        """list of unique session keys"""
        _used: list = []
        return [x for x in self.session_keys if x not in _used and (_used.append(x) or True)]

    def cache_session(self, response: requests.Response, **kwargs):
        """cache cookies and headers to file."""
        _session: dict = {'cookies': dict(), 'headers': dict(), 'params': dict()}

        logger.info(f'session keys: {self.unique_session_keys}')

        _cookies = dict_from_cookiejar(response.cookies)
        if len(_cookies) > 0:
            logger.debug(f'response cookies: {_cookies}')
            _session['cookies'].update({k: v for (k, v) in _cookies.items() if k in self.unique_session_keys})

        _headers = response.headers
        if len(_headers) > 0:
            logger.debug(f'response headers: {_headers}')
            _session['headers'].update({k: v for (k, v) in _headers.items() if k in self.unique_session_keys})

        _params = dict(parse_qsl(urlparse(response.request.url).query))
        if len(_params) > 0:
            logger.debug(f'request params: {json.dumps(_params)}')
            _session['params'].update({k: v for (k, v) in _params.items() if k in self.unique_session_keys})

        if _session:
            logger.info(f'write session cache: {json.dumps(_session)}')
            with open(self.session_store, 'wb') as f:
                pickle.dump(_session, f)

    def reload_session(self):
        """reload cookies and headers from file."""
        _session: dict = dict()
        if os.path.isfile(self.session_store):
            with open(self.session_store, 'rb') as f:
                _session = pickle.load(f)

        logger.info(f'read session cache: {_session}')
        if ('cookies' in _session) and (len(_session['cookies']) > 0):
            self.cookies = cookiejar_from_dict(_session.get('cookies'))
            logger.debug(f'reloaded cookies: {self.cookies}')

        if ('headers' in _session) and (len(_session['headers']) > 0):
            self.headers = _session.get('headers')
            logger.debug(f'reloaded headers: {self.headers}')

        if ('params' in _session) and (len(_session['params']) > 0):
            self.params = _session.get('params')
            logger.debug(f'reloaded params: {self.params}')
