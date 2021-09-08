#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json

from aibuilder.common.auth.constants import _AccessTokenType, _AccessTokenResponseFields
from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.paconnector.connector.resource_provider import PowerAppsRP
from aibuilder.common.paconnector.constants import CustomConnectorConstants as ccConstants
from aibuilder.common.paconnector.constants import PowerAppsSettings


def create_custom_connector(payload: dict, powerapps_url: str, powerapps_basepath: str, powerapps_api_version: str) -> \
        object:
    """
    Creates the custom connector using the payload
    :param powerapps_url: Powerapps url
    :param powerapps_basepath: Powerapps base path
    :param powerapps_api_version: API version
    :param payload: dictionary containing the payload
    :return: dictionary containing the network call response
    """
    credentials_manager = D365Connector().credentials_manager
    credentials_object = credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)
    token = credentials_object.get(_AccessTokenResponseFields.ACCESS_TOKEN.value, 'accessToken not found')
    environment = payload[ccConstants.properties.value][ccConstants.environment.value][ccConstants.name.value]

    connector_settings = {
        ccConstants.powerapps_url.value: powerapps_url or PowerAppsSettings.PROD_URL.value,
        ccConstants.powerapps_base_path.value: powerapps_basepath or PowerAppsSettings.BASE_PATH.value,
        ccConstants.token.value: token,
        ccConstants.powerapps_api_version.value: powerapps_api_version or PowerAppsSettings.API_VERSION.value
    }
    powerapps_rp = PowerAppsRP.get_from_settings(settings=connector_settings)
    response = _create_get_connector(powerapps_rp=powerapps_rp, environment=environment, payload=payload)
    return response


def _create_get_connector(powerapps_rp: PowerAppsRP, environment: str, payload: dict) -> dict:
    """
    Method to create a new connector or retrieve an existing connector.
    :param powerapps_rp: PowerApps RP object
    :param environment: non friendly environment name defined in the payload
    :param payload:  dictionary containing the payload
    :return: dictionary containing the network call response
    """
    # TODO add update connector
    all_connectors_in_env = powerapps_rp.get_all_connectors(environment=environment)['value']
    response = None
    for connector in all_connectors_in_env:
        display_name = connector[ccConstants.properties.value][ccConstants.displayName.value]
        if payload[ccConstants.properties.value][ccConstants.displayName.value] == display_name:
            connector_id = connector[ccConstants.name.value]
            print(f"Connector with {display_name} already exists. Retrieving existing connector")
            response = powerapps_rp.get_connector(environment=environment, connector_id=connector_id)
    if response is not None:
        return response
    else:
        response = powerapps_rp.create_connector(environment=environment, payload=payload)
        print(f"Created connector {payload[ccConstants.properties.value][ccConstants.displayName.value]}")
        return json.loads(response)
