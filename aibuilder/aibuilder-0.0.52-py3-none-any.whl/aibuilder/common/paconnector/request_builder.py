#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import logging
from typing import Any, Optional
from urllib.parse import urljoin, urlencode, urlunparse, quote, urlparse

import requests

from aibuilder.common.paconnector.exceptions import DuplicateModelException, RequestFormatException
from aibuilder.common.paconnector.constants import RequestBuilderConstants

logger = logging.getLogger(__name__)


class _RequestBuilder:
    def __init__(self, url: str, base_path: Optional[str] = "", token: Optional[str] = "",
                 api_version: Optional[str] = None):
        """
        Http client used in connecting to PowerApps environment

        :param url: Url used to extract http scheme and http network location
        :param base_path: Base path of a Http endpoint
        :param token: Bearer token to be added in Http request header
        :param api_version: PowerApps API Version
        """
        if not isinstance(url, str) or len(url) == 0:
            raise ValueError(f"Invalid url. Got {url}")

        (scheme, netloc, _, _, _, _) = urlparse(url)
        self._scheme = scheme
        self._netloc = netloc
        self._base_path = base_path.rstrip('/') + '/'
        self._token = token
        self._api_version = api_version

    def construct_url(self, path: str, query: Optional[dict] = None):
        """
        Builds an endpoint from parameters

        :param path: Path portion of url
        :param query: Any queries necessary for the url
        :return: String- endpoint for a request
        """

        urlparts = [''] * 6

        urlparts[0] = self._scheme
        urlparts[1] = self._netloc
        urlparts[2] = urljoin(self._base_path, path)
        all_query = {}
        if self._api_version:
            all_query = {
                'api-version': self._api_version
            }
        if query:
            all_query.update(query)
        urlparts[4] = urlencode(all_query, quote_via=quote)
        endpoint = urlunparse(urlparts)

        return endpoint

    def request(self, method: RequestBuilderConstants, endpoint: str, headers: Optional[dict] = None,
                payload: Optional[Any] = None):
        """
        Send a request to the given url

        :param method: HTTP request method (POST, GET, etc) represented using RequestBuilderConstants
        :param endpoint: Endpoint url to send request to
        :param headers: Headers to be added to request
        :param payload: Body of request
        :return: Response from request
        """
        all_headers = {}
        if self._token:
            all_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._token}'
            }
        if headers:
            all_headers.update(headers)

        response = requests.request(
            method.value,
            endpoint,
            headers=all_headers,
            json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            if response.status_code == 412:
                raise DuplicateModelException("A model with this name already exists!")
            elif response.status_code == 400:
                raise RequestFormatException(f"Bad Request Exception: {response.text}")
            else:
                raise exception
        return response
