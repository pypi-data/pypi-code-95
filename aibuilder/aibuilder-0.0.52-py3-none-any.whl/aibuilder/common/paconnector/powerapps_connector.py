#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import logging
from typing import Optional

from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.paconnector.constants import PowerAppsSettings
from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.common.paconnector.request_builder import _RequestBuilder
from aibuilder.common.utils import Credentials

logger = logging.getLogger(__name__)


class PowerAppsConnector:
    """
    Class to connect with PowerApps.

    .. code-block:: python
        :caption: **Example code to use PowerApps Object**

        from aibuilder.common.paconnector.powerapps_connector import PowerAppsConnector

        pa_connector = PowerAppsConnector(credentials=None)
        # Proceeds to authenticate using device token since credentials = None
        env_name, environment_url = pa_connector.get_environment_name_and_url(
                            environment_friendly_name=environment_name)

    """
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        :param credentials: Credentials named tuple containing username and password
        """
        self._endpoint = PowerAppsSettings.PROD_URL.value
        self._d365connector = D365Connector()

        self._credentials = credentials
        if self._credentials is not None:
            token = self._d365connector.get_arm_token_with_username_and_password(credentials=credentials)
        else:
            token = self._d365connector.authenticate_with_device_code()

        self._request_builder = _RequestBuilder(url=self._endpoint,
                                                base_path=PowerAppsSettings.BASE_PATH.value,
                                                token=token, api_version=PowerAppsSettings.API_VERSION.value)

    @property
    def d365connector(self) -> D365Connector:
        """
        Sets the Dynamics 365 connector object

        .. code-block:: python
            :caption: **Example code to use PowerApps Object**

            from aibuilder.common.paconnector.powerapps_connector import PowerAppsConnector

            pa_connector = PowerAppsConnector(credentials=None)
            d635_connector = pa_connector.d365connector()
        """
        return self._d365connector

    def get_environment_name_and_url(self, environment_friendly_name: str) -> str:
        """
        Gets PowerApps environment name and environment url using the environment friendly name

        :param environment_friendly_name: Friendly name of PowerApps environment
        :return: environment name for the given environment friendly name
        """
        endpoint = self._request_builder.construct_url(PowerAppsSettings.ENVIRONMENTS.value)
        response = self._request_builder.request(RequestBuilderConstants.GET, endpoint)

        values = response.json().get('value', [])
        for env in values:
            environment_name, organization_url = PowerAppsConnector._get_environment_name_organization_url(env)
            if environment_name == environment_friendly_name:
                logger.info(f'Environment {environment_friendly_name} found!')
                return env['name'], organization_url

        raise ValueError(f"Environment {environment_friendly_name} not found!")

    @staticmethod
    def _get_environment_name_organization_url(environment: dict) -> tuple:
        """
        Extracts environment name and organization url from environment dictionary object returned by PowerApps

        :param environment: Environment dictionary
        :return: A tuple of environment name and organization url. Returns empty strings if environment name or
        organization url is not found in environment dictionary
        """
        environment_name = ""
        organization_url = ""
        if PowerAppsSettings.PROPERTIES.value in environment:
            properties = environment.get(PowerAppsSettings.PROPERTIES.value)
            if PowerAppsSettings.LINKED_ENVIRONMENT_METADATA.value in properties:
                linked_env_metadata = properties.get(PowerAppsSettings.LINKED_ENVIRONMENT_METADATA.value)
                environment_name = linked_env_metadata.get(PowerAppsSettings.FRIENDLY_NAME.value)
                organization_url = linked_env_metadata.get(PowerAppsSettings.INSTANCE_URL.value)

        return environment_name, organization_url
