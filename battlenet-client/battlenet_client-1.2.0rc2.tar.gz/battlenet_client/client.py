"""BattleNet Clients handle the processing on the requests with the Developer Portal API

.. moduleauthor: David "Gahd" Couples <gahdania@gahd.io>
"""

from io import BytesIO
from time import sleep
from urllib.parse import unquote

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from battlenet_client.util import localize
from battlenet_client.exceptions import *
import battlenet_client.constants


class BattleNetClient(OAuth2Session):
    """Handles the communication using OAuth v2 client to Battle.net REST API

    Args:
        region (str): region abbreviation for use with the APIs
        game (dict): the game for the request
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Keyword Args:
        scope (list, optional): the scope or scopes to use during the endpoints that require the Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard

    Attributes:
        tag (str): the region tag (abbreviation) of the client
        api_host (str): the host to use for accessing the API endpoints
        auth_host (str): the host to use for authentication
        render_host (str): the hose to use for images
    """

    def __init__(self, region, game, client_id, client_secret, *, scope=None, redirect_uri=None):

        self._state = None

        try:
            self.tag = getattr(battlenet_client.constants, region)
        except AttributeError:
            if region.strip().lower() in ('us', 'eu', 'kr', 'tw', 'cn'):
                self.tag = region.strip().lower()
            else:
                raise BNetRegionNotFoundError("Region not available")

        self.game = game

        self._client_secret = client_secret

        self.dynamic = f"dynamic-{self.tag}"
        self.static = f"static-{self.tag}"
        self.profile = f"profile-{self.tag}"

        if self.tag == 'cn':
            self.api_host = 'https://gateway.battlenet.com.cn'
            self.auth_host = 'https://www.battlenet.com.cn'
            self.render_host = 'https://render.worldofwarcraft.com.cn'
        elif self.tag == 'kr' or self.tag == 'tw':
            self.api_host = f'https://{self.tag}.api.blizzard.com'
            self.auth_host = 'https://apac.battle.net'
            self.render_host = f'https://render-{self.tag}.worldofwarcraft.com'
        else:
            self.api_host = f'https://{self.tag}.api.blizzard.com'
            self.auth_host = f'https://{self.tag}.battle.net'
            self.render_host = f'https://render-{self.tag}.worldofwarcraft.com'

        if redirect_uri and scope:
            self.auth_flow = 'oauth'
            super().__init__(client_id=client_id, scope=scope, redirect_uri=redirect_uri)
            # set the mode indicator of the client to "Web Application Flow"
        else:
            super().__init__(client=BackendApplicationClient(client_id=client_id))
            # set the mode indicator of the client to "Backend Application Flow"
            self.fetch_token()
            self.auth_flow = None

    def __str__(self):
        return f"{self.game['name']} API Client"

    def __repr__(self):
        return f"{self.__class__.__name__} Instance: {self.game['abbrev']}"

    def api_get(self, *args, **kwargs):
        """Convenience function for the GET method"""
        return self.__endpoint('get', *args, **kwargs)

    def api_post(self, *args, **kwargs):
        """Convenience function for the POST method"""
        return self.__endpoint('post', *args, **kwargs)

    def __endpoint(self, method, uri, locale, namespace, *, retries=5, params=None, headers=None, fields=None):
        """Processes the API request into the appropriate headers for the Requests.request() method

        Args:
            method (str): the HTTP method to use
            uri (str): the URI for the API endpoint
            locale (str): the locale identifier to use with the API
            namespace (str or None): the namespace that is needed for API

        Keyword Args:
            retries (int, optional): the number of retries at getting to the API endpoint (default is 5)
            params (dict, optional): dict of the parameters to be passed via query string to the endpoint
            headers (dict, optional):  Additional headers to sent with the request
            fields (dict, optional): search parameters and values to send
        """

        if params:
            params['locale'] = localize(locale)
        else:
            params = {'locale': localize(locale)}
        
        if fields:
            params.update({key: value for key, value in fields.items()})

        if headers:
            headers['Battlenet-Namespace'] = getattr(self, namespace)
        else:
            headers = {'Battlenet-Namespace': getattr(self, namespace)}

        for _ in range(retries):
            try:
                raw_data = super().request(method, uri, params=params, headers=headers)
                raw_data.raise_for_status()
            except requests.Timeout:
                sleep(2.5)
            except requests.exceptions.HTTPError as error:
                if error.response.status_code == 429:
                    sleep(1.0)

                if error.response.status_code == 404:
                    raise BNetDataNotFoundError(error)

                if error.response.status_code == 403:
                    raise BNetAccessForbiddenError(error)

                raise error
            else:
                if raw_data.headers['content-type'].startswith('application/json'):
                    return raw_data.json()
                else:
                    return BytesIO(raw_data.content)

    def validate_token(self):
        """Checks with the API if the token is good or not.

        Returns:
            bool: True of the token is valid, false otherwise.
        """
        url = f"{self.auth_host}/oauth/check_token"
        data = super().post(url, params={'token': self.access_token}, headers={'Battlenet-Namespace': None})
        return data.status_code == 200 and data.json()['client_id'] == self.client_id

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
