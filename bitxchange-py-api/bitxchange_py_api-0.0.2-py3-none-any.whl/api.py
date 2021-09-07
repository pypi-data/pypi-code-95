import json
from enum import Enum
from urllib.parse import urljoin

import requests

from .__version__ import __version__


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"


class API(object):
    """
    Description: Creates the API class which handles all interactions
    with the exchange endpoint, all auth params are passed into the API
    class from the inheriting class.

    Guide: https://bitxchange-python-api.readthedocs.io/en/latest/index.html

    Args:
        - base_url (str) - base api url, will default if left empty
        - key (str) - users account API key
        - secret (str) - Users account API secret

    KWargs: None
    """

    def __init__(self, base_url, key=None, secret=None):

        self.base_url = base_url
        self.key = key
        self.secret = secret
        self.session = requests.Session()
        self.session.headers.update(
            {"apikey": str(self.key), "secretkey": str(self.secret)}
        )

    def query_exchange(self, url_path, data=None):
        return self.send_request(HTTPMethod.GET, url_path, data=data)

    def send_request(self, http_method, url_path, data=None):
        """Send request params to the exchange for response"""

        from bitxchange.lib.shared_utils import remove_none_values

        if data is None:
            data = {}

        # Join base url and passed in endpoint url
        url = urljoin(self.base_url, url_path)

        params = remove_none_values({"url": url, "data": data})

        # Dispatches request to exchange
        response = self._dispatch_request(http_method)(**params)

        try:
            response_json = response.json()
        except (ValueError, json.JSONDecodeError):
            return {"data": response.text}

        if response_json:
            return response_json

        raise ValueError("Response from exchange is empty!")

    def _dispatch_request(self, http_method):
        """Returns session type based on send_request params"""

        method_map = {
            HTTPMethod.GET: self.session.get,
            HTTPMethod.POST: self.session.post,
        }

        if http_method not in method_map:
            raise ValueError(f"{http_method} not supported!")

        return method_map[http_method]
