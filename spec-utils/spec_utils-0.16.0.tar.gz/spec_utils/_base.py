from __future__ import annotations
from typing import Optional, Union, Dict, List, Any

import requests
from urllib.parse import urlparse, urlencode, urljoin, quote

try:
    from ._utils import Decorators
except ImportError:
    from _utils import Decorators


class APIKeyClient:

    __name__ = None
    
    def __init__(
        self,
        url: str,
        apikey: str,
        session: Optional[requests.Session] = None,
        **kwargs
    ) -> None:
        """ Create a connector for SPECManager API using recived parameters.

        Args:
            url (str): Full url to SPECManager API
            apikey (str): API-Key provided by SPEC SA
            session (Optional[requests.Session], optional):
                Optional requests session.
                Defaults to None
        """

        self.client_url = urlparse(url)
        self.client_fullpath = url
        self.apikey = apikey
        self.session = session
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
            "apikey": apikey
        }
        self.kwargs_ = kwargs

    def __eq__(self, o: object) -> bool:
        return self.apikey == o.apikey
    
    def __ne__(self, o: object) -> bool:
        return self.apikey != o.apikey

    def __str__(self) -> str:
        return f'{self.__name__} Client for {self.client_fullpath}'

    def __repr__(self) -> str:
        return "{}(url='{}', apikey='{}', session={})".format(
            self.__class__.__name__,
            self.client_fullpath,
            self.apikey,
            self.session
        )

    def __enter__(self, *args, **kwargs) -> APIKeyClient:
        self.start_session()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close_session()

    def start_session(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def close_session(self):
        self.session.close()
        self.session = None

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