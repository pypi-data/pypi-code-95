"""BattleNet Clients handle the processing on the requests with the Developer Portal API

.. moduleauthor: David "Gahd" Couples <gahdania@gahd.io>
"""

from io import BytesIO
from time import sleep
from urllib.parse import unquote

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .util import localize


class BattleNetClient(OAuth2Session):
    """Handles the communication using OAuth v2 client to Battle.net REST API

    Args:
        region (str): region abbreviation for use with the APIs
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list, optional): the scope or scopes to use during the endpoints that require the Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str, optional): the client ID from the developer portal
        client_secret (str, optional): the client secret from the developer portal

    Attributes:
        tag (str): the region tag (abbreviation) of the client
        dynamic_ns (str): the namespace to use for dynamic elements of the API (ie: characters, and guilds)
        static_ns (str): the namespace to use for static elements of the API (ie: realms, connected_realms)
        profile_ns (str): the namespace to use for profile based elements (ie: player info, protected char info)
        api_host (str): the host to use for accessing the API endpoints
        auth_host (str): the host to use for authentication
        render_host (str): the hose to use for images
        locale (str): the localization, if any, of the client

    """

    def __init__(self, region, game, client_id, client_secret, *, release=None, scope=None, redirect_uri=None):

        self._state = None
        self.tag = region.strip().lower()
        self.game = game

        self._client_secret = client_secret

        self.release = release.lower()

        if release:
            self.dynamic_ns = f"dynamic-{self.release}-{self.tag}"
            self.static_ns = f"static-{self.release}-{self.tag}"
            self.profile_ns = f"profile-{self.release}-{self.tag}"
        else:
            self.dynamic_ns = f"dynamic-{self.tag}"
            self.static_ns = f"static-{self.tag}"
            self.profile_ns = f"profile-{self.tag}"

        if self.tag == 'cn':
            self.api_host = 'https://gateway.battlenet.com.cn'
            self.auth_host = 'https://www.battlenet.com.cn'
            self.render_host = None  # may need someone playing on the chinese client to help me
        elif self.tag == 'kr' or self.tag == 'tw':
            self.api_host = f'https://{self.tag}.api.blizzard.com'
            self.auth_host = f'https://apac.battle.net'
            self.render_host = f'https://render-{self.tag}.worldofwarcraft.com'
        else:
            self.api_host = f'https://{self.tag}.api.blizzard.com'
            self.auth_host = f'https://{self.tag}.battle.net'
            self.render_host = f'https://render-{self.tag}.worldofwarcraft.com'

        if redirect_uri and scope and 'openid' not in scope:
            self.__auth_flow = 'oauth'
            super().__init__(client_id=client_id, scope=scope, redirect_uri=redirect_uri)
            # set the mode indicator of the client to "Web Application Flow"

        else:
            super().__init__(client=BackendApplicationClient(client_id=client_id))
            # set the mode indicator of the client to "Backend Application Flow"
            self.fetch_token()
            self.__auth_flow = None

    @property
    def auth_flow(self):
        return self.__auth_flow

    @auth_flow.setter
    def auth_flow(self, value=None):
        self.__auth_flow = value

    def validate_token(self, locale=None):
        """Checks with the API if the token is good or not.

        Args:
            locale (str): localization desired.

        Returns:
            bool: True of the token is valid, false otherwise.
        """
        url = f"{self.auth_host}/oauth/check_token"
        return self.get(url, locale=locale)

    def authorization_url(self, **kwargs):
        """Prepares and returns the authorization URL to the Battle.net authorization servers

        Returns:
            str: the URL to the Battle.net authorization server
        """
        if not self.auth_flow:
            raise ValueError("Requires Authorization Workflow")

        auth_url = f"{self.auth_host}/oauth/authorize"
        authorization_url, self._state = super().authorization_url(url=auth_url, **kwargs)
        return unquote(authorization_url)

    def fetch_token(self, **kwargs):
        token_url = f"{self.auth_host}/oauth/token"
        super().fetch_token(token_url=token_url, client_id=self.client_id, client_secret=self._client_secret,
                            **kwargs)

    def __request(self, method, uri, *, namespace=None, locale=None, retries=5, fields=None, headers=None,
                  stream=False):

        """Sends the request to given `uri`

        Args:
            method (str): HTTP request method: get or post
            uri (str): URI of the endpoint
            namespace (str, optional): Certain API endpoints they require a namespace to work. Default is None
            locale (str, optional): localization to use for the API endpoint.
            retries (int, optional): the number of retries until the attempt is cancelled.  Default is 5 retries
            fields (list, optional): the fields to retrieve from the API (varies by endpoint) Default is None
            headers (dict, optional): additional headers to add to the request
            stream (bool, optional): instructs the client that the client receive parts of the data at a time when True,
                otherwise False

        Returns:
            dict or :obj:`BytesIO`: json decoded dict from the API or the data from a media source,
                or binary data (ie: an emblem image)

        Raises:
            HTTPError: on all errors from the Battle.net REST API
        """
        raw_data = None

        if not uri.startswith('http'):
            url = f'{self.api_host}/{uri.lower()}'
        else:
            url = uri

        if fields and isinstance(fields, (list, tuple)):
            fields = ','.join(str(field) for field in fields)

        if namespace and self.tag == 'cn':
            namespace = None

        if locale:
            locale = localize(locale)
        else:
            locale = self.standard

        if method == "post":
            params = {'locale': locale, 'fields': fields}
            headers['Battlenet-Namespace'] = namespace
        else:
            params = {'locale': locale, 'fields': fields, 'namespace': namespace}

        for _ in range(retries):
            try:
                raw_data = super().request(method, url, headers=headers, stream=stream, params=params)
                raw_data.raise_for_status()
            except requests.Timeout:
                sleep(2.5)
            except requests.exceptions.HTTPError as error:
                if error.response.status_code == 429:
                    sleep(1.0)
                else:
                    raise error
            else:
                if raw_data.headers['content-type'].startswith('application/json'):
                    return raw_data.json()
                else:
                    return BytesIO(raw_data.content)

    def get(self, uri, **kwargs):
        return self.__request("GET", uri, **kwargs)

    def post(self, uri, **kwargs):
        return self.__request("POST", uri, **kwargs)

    def get_user_info(self, locale=None):
        """Returns the user info

        Args:
            locale (str): localization to use

        Returns:
            dict: the json decoded information for the user (user # and battle tag ID)
        """
        if not self.auth_flow:
            raise ValueError("Requires Authorization Workflow")

        url = f"{self.auth_host}/oauth/userinfo"
        return self.post(url, locale=locale)
