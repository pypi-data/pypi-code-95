"""moose connect"""
import copy
import os
from base64 import b64encode

from requests_toolbelt import user_agent
from requests.utils import add_dict_to_cookiejar
import logging

from moosetools import __app__, __version__
from moosetools.connect import headers
from moosetools.connect.sessions import AppSession

"""default logger"""
logger = logging.getLogger(__name__)

"""default directory to store cookies and other cache"""
_default_store_: os.path = os.getcwd()

"""user-agent for connection"""
_user_agent_header_: dict = {'User-Agent': user_agent(__app__, __version__)}

"""default list of keys to cache"""
_default_session_keys_: list = ['Authorization']


def connect_json_app(base_url: str, username: str = None, password: str = None, force_basic: bool = False,
                     session_cookies: dict = None, session_headers: dict = None, session_params: dict = None, session_keys: list = None,
                     store: os.path = _default_store_) -> AppSession:
    """create app session with base_url of api server

    Parameters
    ----------
    base_url
    username
    password
    force_basic
    session_cookies
    session_headers
    session_params
    session_keys
    store

    Returns
    -------
    AppSession
    """
    _session = copy.deepcopy(AppSession)(base_url=base_url, app=__app__, store=store)

    """update user agent header"""
    _session.headers.update(_user_agent_header_)
    logger.debug(f'add user_agent_header: {_session.headers}')

    """add json headers"""
    _session.headers.update(headers.json_content_accept)
    logger.debug(f'add json headers: {_session.headers}')

    """add session params"""
    if (session_params is not None) and (len(session_params) > 0):
        _session.params.update(session_params)
        logger.debug(f'add session params: {_session.params}')

    """add session headers"""
    if (session_headers is not None) and (len(session_headers) > 0):
        _session.headers.update(session_headers)
        logger.debug(f'add session headers: {_session.headers}')

    """add session cookies"""
    if (session_cookies is not None) and (len(session_cookies) > 0):
        _session.cookies.update(session_cookies)
        logger.debug(f'add session cookies: {_session.cookies.get_dict()}')

    """session keys in headers or params to save"""
    if (session_keys is not None) and (type(session_keys) is list):
        _session.session_keys = session_keys
        logger.info(f'session search keys: {_session.unique_session_keys}')

    """set basic authentication"""
    if (username is not None) and (password is not None):
        _session.auth = (username, password)
        logger.debug(f'basic auth for {username}')
        if force_basic:
            _basic_auth = b64encode(f'{username}:{password}')
            _session.headers.update({'Authentication': f'Basic {_basic_auth}'})
            logger.debug(f'force basic auth for {username}')

    logger.info(f'init session params: {_session.params}')
    logger.info(f'init session headers: {_session.headers}')
    logger.info(f'init session cookies: {_session.cookies.get_dict()}')
    """add cache_session hook"""
    _session.hooks['response'].append(_session.cache_session)
    logger.debug(f'cache_session hook added')

    return _session
