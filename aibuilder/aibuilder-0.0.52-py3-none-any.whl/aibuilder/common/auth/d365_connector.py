#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import logging

import adal

from aibuilder.common.auth.constants import _AccessConfig, _AccessTokenResponseFields, _AccessTokenType
from aibuilder.common.auth.token_cache_manager import TokenCacheManager
from aibuilder.common.utils import Credentials

logger = logging.getLogger(__name__)


class D365Connector:
    """
    D365Connector is used to connect to a Dynamics CRM 365 Organization

     .. code-block:: python
        :caption: **Example code to use D365Connector Object**

        from aibuilder.common.auth.d365_connector import D365Connector

        d365_connector = D365Connector()

    """

    def __init__(self):
        self._auth_context = adal.AuthenticationContext(authority=_AccessConfig.AUTHORITY.value)
        self._credentials_manager = TokenCacheManager()

    @property
    def credentials_manager(self) -> TokenCacheManager:
        """
        Returns credential manager object

        """
        return self._credentials_manager

    def get_arm_token_with_username_and_password(self, credentials: Credentials) -> str:
        """
        Authenticate using username and password named tuple

        .. code-block:: python
            :caption: **Example code to get arm token based on credentials**

            from aibuilder.common.utils import Credentials
            from aibuilder.common.auth.d365_connector import D365Connector

            credentials = Credentials(username="your_username", password="your_password")
            arm_token = D365Connector.get_arm_token_with_username_and_password(credentials=credentials)

        :param credentials: dict containing username and password
        :return: Return an ARM token
        """
        if not isinstance(credentials, Credentials):
            raise TypeError(f"Expected Credentials namedtuple, but got {type(credentials)}")

        arm_token = self._get_token_with_username_password(credentials=credentials)

        self.credentials_manager.save_token(token_dict=arm_token, token_type=_AccessTokenType.ARM_TOKEN)
        return arm_token.get(_AccessTokenResponseFields.ACCESS_TOKEN.value)

    def authenticate_with_dynamics_crm(self, organization_url: str) -> str:
        """
        Retrieves token if expired or credentials do not yet exist

         .. code-block:: python
            :caption: **Example code to retrieve the token if it is expired or non existent**

            from aibuilder.common.auth.d365_connector import D365Connector

            organization_url = "https://your-organization-url-from-powerapps.com"
            arm_token = D365Connector.authenticate_with_dynamics_crm(organization_url=organization_url)

        :param organization_url: Org url
        :return: Valid user token
        """
        crm_token_dict = self.credentials_manager.get_token(token_type=_AccessTokenType.CRM_TOKEN)
        is_expired = not self.credentials_manager.is_valid_token(crm_token_dict)

        # TODO: Check why a protected variable is accessed to know if auth cache is empty
        if is_expired or not self._has_valid_auth_context_cache():
            self._refresh_authentication_context()

        if is_expired or not crm_token_dict:
            crm_token_dict = self._refresh_crm_token(organization_url=organization_url)

        return crm_token_dict.get(_AccessTokenResponseFields.ACCESS_TOKEN.value)

    def authenticate_with_device_code(self, force_authenticate=False):
        """
        Authenticates user by sending them a code for their device

         .. code-block:: python
            :caption: **Example code to get arm token based on device based token authentication**

            from aibuilder.common.auth.d365_connector import D365Connector

            arm_token = D365Connector.authenticate_with_device_code()

        :param force_authenticate: Boolean whether user needs to be authenticated again
        :return: Valid user token
        """
        credentials = self._credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)
        is_expired = not self.credentials_manager.is_valid_token(credentials)
        if not credentials or is_expired or force_authenticate:
            arm_token = self._get_token_with_device_code()
            self._credentials_manager.save_token(token_dict=arm_token, token_type=_AccessTokenType.ARM_TOKEN)
            return arm_token.get(_AccessTokenResponseFields.ACCESS_TOKEN.value, 'accessToken not found')
        return credentials.get(_AccessTokenResponseFields.ACCESS_TOKEN.value, 'accessToken not found')

    def _has_valid_auth_context_cache(self) -> bool:
        """Checks if the auth context cache is valid

        :return: True if auth context cache has value else returns False
        """
        if self._auth_context and self._auth_context.cache._cache:
            return True
        return False

    def _refresh_crm_token(self, organization_url: str) -> dict:
        """
        Refreshes CRM token

        :param organization_url: Org url
        :return: Dictionary containing crm token and token metadata
        """
        arm_token_dict = self.credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)

        user_id = arm_token_dict.get(_AccessTokenResponseFields.USER_ID.value)

        crm_token_dict = self._auth_context.acquire_token(resource=organization_url,
                                                          client_id=_AccessConfig.CLIENT_ID.value,
                                                          user_id=user_id)

        self.credentials_manager.save_token(token_dict=crm_token_dict,
                                            token_type=_AccessTokenType.CRM_TOKEN)

        return crm_token_dict

    def _refresh_authentication_context(self):
        """
        This method is used to refresh ADAL Auth context.
        If auth context cache is empty or crm token has expired, we will have to get new auth context

        """
        arm_token_dict = self.credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)
        token_cache = adal.TokenCache(json.dumps([arm_token_dict]))
        self._auth_context = adal.AuthenticationContext(authority=_AccessConfig.AUTHORITY.value, cache=token_cache)

    def _get_token_with_username_password(self, credentials: Credentials) -> dict:
        """
        Call Azure Active Directory acquire token method using username and password

        :param credentials: Credentials object containing username and password
        :return: Dictionary containing token and token metadata returned by Azure Active Directory
        """
        arm_token = self._auth_context.acquire_token_with_username_password(
            resource=_AccessConfig.RESOURCE.value,
            username=credentials.username,
            password=credentials.password,
            client_id=_AccessConfig.CLIENT_ID.value)

        return arm_token

    def _get_token_with_device_code(self) -> dict:
        """
        :return: Dictionary containing token and token metadata returned by Azure Active Directory
        """
        code = self._auth_context.acquire_user_code(resource=_AccessConfig.RESOURCE.value,
                                                    client_id=_AccessConfig.CLIENT_ID.value)
        print(code['message'])
        arm_token = self._auth_context.acquire_token_with_device_code(resource=_AccessConfig.RESOURCE.value,
                                                                      client_id=_AccessConfig.CLIENT_ID.value,
                                                                      user_code_info=code)
        return arm_token

    def get_token_using_refresh_token(self, resource: str) -> dict:
        """
        Get token for any resource using refresh token. This method can be used to get access token for any resource
        using refresh token of a resource.

        :param resource: Url of resource
        :return: Dictionary containing access token, user id and other token parameters
        """
        arm_token_dict = self.credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)

        return self._auth_context.acquire_token_with_refresh_token(
            refresh_token=arm_token_dict.get(_AccessTokenResponseFields.REFRESH_TOKEN.value),
            client_id=_AccessConfig.CLIENT_ID.value, resource=resource)
