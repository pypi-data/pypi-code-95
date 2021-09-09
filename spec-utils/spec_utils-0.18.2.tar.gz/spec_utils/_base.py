from __future__ import annotations
from json.decoder import JSONDecodeError
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Optional, Union, Dict, List, Any
from inspect import signature
from urllib.parse import urlparse, urlencode, urljoin, quote

import requests

try:
    from ._utils import Decorators
except ImportError:
    from _utils import Decorators


class HTTPClient:
    __name__: Optional[str] = None

    def __init__(
        self,
        *,
        url: Union[str, Path],
        session: Optional[requests.Session] = None
    ) -> None:
        # base
        self.url = url
        self.session = session
        
        # needs
        self.client_url = urlparse(url)
        self.client_fullpath = url

        # unset
        self.headers = None

    def __str__(self) -> str:
        return f'{self.__name__} Client for {self.client_fullpath}'

    def __repr__(self) -> str:
        try:
            return "{class_}({params})".format(
                class_=self.__class__.__name__,
                params=', '.join([
                    "{attr_name}={quote}{attr_val}{quote}".format(
                        attr_name=attr,
                        quote="'" if type(getattr(self, attr)) == str else "",
                        attr_val=getattr(self, attr)
                    )
                    for attr in signature(self.__init__).parameters
                ])
            )
        except:
            return super().__repr__()


class OAuthClient(HTTPClient):

    def __init__(
        self,
        *,
        url: Union[str, Path],
        username: str,
        pwd: str,
        session: Optional[requests.Session] = None,
    ) -> None:
        super().__init__(url=url, session=session)

        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

    def __eq__(self, o: OAuthClient) -> bool:
        return self.url == o.url and self.username == o.username
    
    def __ne__(self, o: OAuthClient) -> bool:
        return self.url == o.url or self.username != o.username

    @property
    def is_connected(self):
        """ Overwrite this property according to your need. """
        raise NotImplementedError("This method must be overloaded to work.")

    def login(self) -> None:
        """ Overwrite this method according to your need. """
        raise NotImplementedError("This method must be overloaded to work.")

    def logout(self) -> None:
        """ Overwrite this method according to your need. """
        raise NotImplementedError("This method must be overloaded to work.")

    def relogin(self) -> None:
        """ Overwrite this method according to your need. """
        raise NotImplementedError("This method must be overloaded to work.")

    def __enter__(self, *args, **kwargs) -> OAuthClient:
        self.start_session()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close_session()

    def start_session(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # login
        self.login()

    def refresh_session(self) -> None:
        self.session.headers.update(self.headers)

    def close_session(self):
        self.logout()
        if self.session != None:
            self.session.close()
        self.session = None

    @Decorators.ensure_session
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict, List, requests.Response]:
        """
        Sends a GET request to visma url.

        :param path: path to add to URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # prepare url
        url = urljoin(self.client_url.geturl(), path)

        # consulting nettime
        response = self.session.get(url=url, params=params, **kwargs)

        # if session was closed, reconect client and try again
        if response.status_code == 401 and self.session_expired:
            self.relogin()
            return self.get(path=path, params=params, **kwargs)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError({
                "status": response.status_code,
                "detail": response.text
            })

        # if request is stream type, return all response
        if kwargs.get("stream"):
            return response

        # to json
        return response.json()

    @Decorators.ensure_session
    def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Sends a POST request to visma url.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the 
            :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # prepare url
        url = urljoin(self.client_url.geturl(), path)

        # consulting visma
        response = self.session.post(
            url=url,
            params=params,
            data=data,
            json=json,
            **kwargs
        )

        # if session was closed, reconect client and try again
        if response.status_code == 401 and self.session_expired:
            self.relogin()
            return self.post(
                path=path,
                params=params,
                data=data,
                json=json,
                **kwargs
            )

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError({
                "status": response.status_code,
                "detail": response.text
            })

        try:
            return response.json()
        except JSONDecodeError:
            return response.text


class APIKeyClient(HTTPClient):
    
    def __init__(
        self,
        *,
        url: Union[str, Path],
        apikey: str,
        session: Optional[requests.Session] = None,
    ) -> None:
        super().__init__(url=url, session=session)
        
        self.apikey = apikey
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
            "apikey": apikey
        }

    def __eq__(self, o: object) -> bool:
        return self.url == o.url and self.apikey == o.apikey
    
    def __ne__(self, o: object) -> bool:
        return self.url == o.url or self.apikey != o.apikey

    def __enter__(self, *args, **kwargs) -> APIKeyClient:
        self.start_session()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close_session()

    def start_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def close_session(self):
        if self.session != None:
            self.session.close()
        self.session = None

    @property
    def is_connected(self):
        return self.session != None

    @Decorators.ensure_session
    def get(
        self,
        path: str,
        params: dict = None,
        **kwargs
    ) -> Union[Dict, List, requests.Response]:
        """ Sends a GET request to API Client.

        Args:
            path (str): Path to add to client full path URL
            params (dict, optional):
                Data to send in the query parameters of the request.
                Defaults to None.

        Raises:
            ConnectionError: If response status not in range(200, 300)

        Returns:
            Union[Dict, List]: JSON Response if request is not stream.
            requests.Response: If request is stream.
        """

        # prepare url
        url = urljoin(self.client_fullpath, path)

        # consulting certronic
        response = self.session.get(url=url, params=params, **kwargs)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError({
                'status': response.status_code,
                'detail': response.text
            })

        # if request is stream type, return all response
        if kwargs.get("stream"):
            return response

        # return json response
        return response.json()

    @Decorators.ensure_session
    def post(
        self,
        path: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        **kwargs
    ) -> Union[Dict, List]:
        """ Sends a POST request to SPEC Manager url.

        Args:
            path (str): Path to add to client full path URL
            params (dict, optional):
                Data to send in the query parameters of the request.
                Defaults to None.
            data (dict, optional):
                Form Data to send in the request body.
                Defaults to None.
            json (dict, optional):
                JSON Data to send in the request body.
                Defaults to None.

        Raises:
            ConnectionError: If response status not in range(200, 300)

        Returns:
            Union[Dict, List]: JSON Response
        """

        # prepare url
        url = urljoin(self.client_fullpath, path)

        # consulting certronic
        response = self.session.post(
            url=url,
            params=urlencode(params, quote_via=quote),
            data=data,
            json=json,
            **kwargs
        )

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError({
                'status': response.status_code,
                'detail': response.text
            })

        # return json response
        return response.json()