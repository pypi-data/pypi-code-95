import json
import logging

import requests
from requests import ConnectTimeout, ReadTimeout
from requests.auth import HTTPBasicAuth

from library_nsxt.exceptions import APIError

_URL_API = "https://%s/api/v1"
_URL_SECURITY_API = "https://%s/policy/api/v1"


class NSXTAPISession:
    """Defines methods to make HTTP requests and receive responses"""

    def __init__(self, host, user, password, timeout=None):
        """
        Instantiates a new NSX-T session.

        :param str host: The host of the NSX-T API
        :param str user: The user of the BasicAuth used to connect to the NSX-T API
        :param str password: The user of the BasicAuth used to connect to the NSX-T API
        :param float or None timeout: The default max time to wait for each request before an error is thrown.
        """
        self.__host = host
        self.__user = user
        self.__password = password
        self.__timeout = timeout
        self._logger = logging.getLogger("%s@%s" % (self.__class__.__name__, host))

    def check(self, path, security_api=False):
        """
        Requests a model or resource from the API and returns true if there was no error retrieving it. Will never
        raise an error.

        :param str path: The url path of the item to be checked.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        :return: True if the element exists, false otherwise.
        :rtype: bool
        """
        try:
            self.execute_api_call("GET", path, body=None, security_api=security_api)
            return True
        except APIError:
            return False

    def get(self, path, security_api=False, body_payload=None):
        """
        Requests a model or resource from the API.

        :param str path: The url path of the item to be got.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        :param json body_payload: the payload to pass to the api call if requested
        :return: The request response as a dictionary if it's a JSON, or as a String if not.
        :rtype: dict or str
        """
        return self.execute_api_call("GET", path, body=body_payload, security_api=security_api)

    def post(self, path, body, security_api=False):
        """
        Creates a model or resource from the API.

        :param str path: The url path of the item to be posted.
        :param dict or str body: Body of the request. If body is a dictionary it will be parsed into a JSON.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        """
        self.execute_api_call("POST", path, body=body, security_api=security_api)

    def put(self, path, body, security_api=False):
        """
        Replaces or inserts a model or resource from the API.

        :param str path: The url path of the item to be put.
        :param dict or str body: Body of the request. If body is a dictionary it will be parsed into a JSON.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        """
        self.execute_api_call("PUT", path, body=body, security_api=security_api)

    def patch(self, path, body, security_api=False):
        """
        Updates a model or resource from the API.

        :param str path: The url path of the item to be patched.
        :param dict or str body: Body of the request. If body is a dictionary it will be parsed into a JSON.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        """
        self.execute_api_call("PATCH", path, body=body, security_api=security_api)

    def delete(self, path, security_api=False):
        """
        Deletes a model or resource from the API.

        :param str path: The url path of the item to be deleted.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        """
        self.execute_api_call("DELETE", path, body=None, security_api=security_api)

    def execute_api_call(self, method, path, body=None, security_api=False):
        """
        Executes an call to a REST API with the described method, basic authentication and set parameters.

        :param str method: The method to use. Supported methods are GET, POST, PUT, PATCH and DELETE.
        :param str path: The url path of the item to be checked.
        :param dict or str or None body: Body of the request. If body is a dictionary it will be parsed into a JSON.
        :param bool security_api: If true, the session will check for the resource in the policy api. Default is False.
        :return: The request response as a dictionary if it's a JSON, or as a String if not.
        :rtype: dict or str
        :raises APIError: If the request cannot be made or the operation cannot be completed.
        """
        url = (_URL_SECURITY_API if security_api else _URL_API) % self.__host + path
        auth = HTTPBasicAuth(self.__user, self.__password)
        headers = {"content-type": "application/json"} if hasattr(body, "items") else None
        data = json.dumps(body) if hasattr(body, "items") else body

        self._logger.debug("Calling %s: %s" % (method, url))
        try:
            response = requests.request(method, url, auth=auth, headers=headers, data=data,
                                        verify=False, timeout=self.__timeout)
        except (ConnectTimeout, ReadTimeout):
            raise APIError("Requester timed out for request %s: %s" % (method, path))

        if not 200 <= response.status_code < 300:
            try:
                response_body = response.json()
                raise APIError(response_body["error_message"], response_body["error_code"])
            except (TypeError, OverflowError, ValueError, AttributeError, KeyError):
                raise APIError("%s at %s: %s" % (response.reason, method, path), response.status_code)

        try:
            return response.json()
        except ValueError:
            return response.text
