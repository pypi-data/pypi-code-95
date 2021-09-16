import logging
import requests
import json

from pyopencell import helpers
from pyopencell import exceptions


logger = logging.getLogger(__name__)


class Client(object):
    """ PyOpenCell class
    """

    def __init__(self):
        self.baseurl = helpers.getenv_or_fail('OPENCELL_BASEURL')
        self.username = helpers.getenv_or_fail('OPENCELL_USER')
        self.password = helpers.getenv_or_fail('OPENCELL_PASSWORD')

    def get(self, route, **kwargs):
        """ Send a GET HTTP requests

        Args:
            route (str): String with the route to the endpoint

        Return:
            **response**: Return the response object
        """
        return self._send_request(
            verb="GET",
            url=self._format_url(route),
            params=kwargs,
        ).json()

    def post(self, route, body):
        """ Send a POST HTTP requests

        Args:
            route (str): String with the route to the endpoint
            body (dict): Dict with the body of the request to send

        Return:
            **response**: Return the response object
        """
        return self._send_request(
            verb="POST",
            url=self._format_url(route),
            payload=body
        ).json()

    def put(self, route, body):
        """ Send a PUT HTTP requests

        Args:
            route (str): String with the route to the endpoint
            body (dict): Dict with the body of the request to send

        Return:
            **response**: Return the response object
        """
        return self._send_request(
            verb="PUT",
            url=self._format_url(route),
            payload=body
        ).json()

    def delete(self, route):
        """ Send a DELETE HTTP requests

        Args:
            route (str): String with the route to the endpoint
            body (dict): Dict with the body of the request to send

        Return:
            **response**: Return the response object
        """
        return self._send_request(
            verb="DELETE",
            url=self._format_url(route)
        )

    def _format_url(self, path):
        return "{url}{path_prefix}{path}".format(
            url=self.baseurl,
            path_prefix="/api/rest",
            path=path)

    def _send_request(self, verb, url, payload=None, params={}):
        """send the API request using the *requests.request* method

        Args:
            payload (dict)

        Raises:
            OTRSHTTPError:
            ArgumentMissingError

        Returns:
            **requests.Response**: Response received after sending the request.

        .. note::
            Supported HTTP Methods: DELETE, GET, HEAD, PATCH, POST, PUT
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        json_payload = None
        if payload:
            json_payload = json.dumps(payload)

        logger.info("{verb} {url} \n {body}".format(verb=verb, url=url, body=payload))
        try:
            response = requests.request(verb.upper(),
                                        url,
                                        headers=headers,
                                        data=json_payload,
                                        params=params,
                                        auth=(self.username, self.password))
        except Exception as err:
            raise exceptions.PyOpenCellHTTPException(err)

        if self._check_response_error(response):
            raise exceptions.PyOpenCellAPIException(
                verb=response.request.method,
                url=response.request.url,
                status=response.status_code,
                body=response.content or ""
            )

        return response

    @staticmethod
    def _check_response_error(response):
        """ Check the response of the OpenCell API. Not always the status code match with the real
        status of the response. We found some cases that response has a 200 OK status but in the
        body we find an error message instead of the expected response.

        We found the next cases:
        * Status 200 but in the body:
          - response.content with "errorCode".
          - response.content with "status" equal to "FAIL".
        * Status of error (>= 400)
        """
        if response.status_code >= 400:
            return True

        if response.content:
            r_json = response.json()
            if "errorCode" in r_json or ("status" in r_json and r_json.get('status') == 'FAIL'):
                return True
        return False
