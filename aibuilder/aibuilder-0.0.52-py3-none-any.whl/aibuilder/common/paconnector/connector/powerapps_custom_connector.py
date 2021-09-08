#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import copy
from typing import Optional

from aibuilder.common.auth.constants import _AccessTokenType, _AccessTokenResponseFields, _AccessConfig
from aibuilder.common.auth.d365_connector import D365Connector
from aibuilder.common.constants import GraphClientConstants
from aibuilder.common.graph_client import _GraphClient
from aibuilder.common.paconnector.connector.connector_request_builder import CustomConnectorRequestBuilder
from aibuilder.common.paconnector.connector.exceptions import UpdateConnectorException, ConnectionCreationException
from aibuilder.common.paconnector.connector.resource_provider import PowerAppsRP
from aibuilder.common.paconnector.constants import CustomConnectorConstants as ccConstants
from aibuilder.common.paconnector.constants import PowerAppsSettings
from aibuilder.models.open_api_specification import _OpenAPISpecification


class PowerAppsCustomConnector:
    def __init__(self, environment_name: str):
        self._d365_connector = D365Connector()
        self._environment_name = environment_name

        self._powerapps_rp = self._get_powerapps_resource_provider()

    def _get_powerapps_resource_provider(self) -> PowerAppsRP:
        """
        Creates a PowerApps resource provider object required for PowerApps custom connector

        :return: PowerApps resource provider object
        """

        arm_token = self._d365_connector.credentials_manager.get_token(token_type=_AccessTokenType.ARM_TOKEN)

        arm_access_token = arm_token.get(_AccessTokenResponseFields.ACCESS_TOKEN.value, 'accessToken not found')

        powerapps_rp_settings = {
            ccConstants.powerapps_url.value: PowerAppsSettings.PROD_URL.value,
            ccConstants.powerapps_base_path.value: PowerAppsSettings.BASE_PATH.value,
            ccConstants.token.value: arm_access_token,
            ccConstants.powerapps_api_version.value: PowerAppsSettings.API_VERSION.value
        }

        return PowerAppsRP.get_from_settings(settings=powerapps_rp_settings)

    def _get_connector_id(self, connector_name: str) -> Optional[str]:
        """
        Returns connector id using connector display name

        :param connector_name: Connector display name
        :return: Connector id (guid) if connector exists
        """
        all_connectors_in_env = self._powerapps_rp.get_all_connectors(environment=self._environment_name)['value']

        for connector in all_connectors_in_env:
            display_name = connector[ccConstants.properties.value][ccConstants.displayName.value]
            if connector_name == display_name:
                # Get connector API returns connector id as connector name
                return connector[ccConstants.name.value]

    def _setup_connector(self, connector_swagger: dict, override: bool) -> Optional[dict]:
        """
        Retrieve an existing connector or creates a new connector. An existing connector can be updated by setting
        override to True

        :param connector_swagger: Swagger required for creating a connector
        :param override: Override connector if it already exists
        :return: Dictionary containing connector information returned by the network call
        """
        connector_name = connector_swagger[ccConstants.properties.value][ccConstants.displayName.value]
        connector_id = self._get_connector_id(connector_name=connector_name)

        # Get connector using connector id. If connector id is None, get connector returns None
        response = self._powerapps_rp.get_connector(environment=self._environment_name,
                                                    connector_id=connector_id)

        # If connector exists and needs to be updated
        if response and override:
            # Display name cannot be updated, removing display name from update request
            update_connector_swagger = copy.deepcopy(connector_swagger)
            if ccConstants.displayName.value in update_connector_swagger[ccConstants.properties.value]:
                update_connector_swagger[ccConstants.properties.value].pop(ccConstants.displayName.value)

            update_status = self._powerapps_rp.update_connector(environment=self._environment_name,
                                                                connector_id=connector_id,
                                                                payload=update_connector_swagger)
            if not update_status:
                raise UpdateConnectorException("Connector update failed")

        # If Connector doesn't exist or deleted, create a new one
        if response is None:
            response = self._powerapps_rp.create_connector(environment=self._environment_name,
                                                           payload=connector_swagger)
            print(f"Created connector {connector_name}")

        return response

    @staticmethod
    def _construct_connection_request_body(api_key: str, environment_object: Optional[dict] = None) -> dict:
        properties = {ccConstants.connection_parameters.value: None}

        # if api key is passed, update connection properties
        if api_key:
            connection_parameters = {
                ccConstants.api_key.value: api_key
            }
            properties[ccConstants.connection_parameters.value] = connection_parameters

        # If environment object is passed, add environment object
        # For update connection environment object should not be passed to this method
        if environment_object:
            properties.update({ccConstants.environment.value: environment_object})

        connection_request_body = {
            ccConstants.properties.value: properties
        }

        return connection_request_body

    def _setup_connection(self, connector_name: str, connection_name: str, api_key: str, connector_id: str,
                          environment_object: dict, override: bool, org_url, cds_token) -> dict:
        """
        Create a connection (an instance of connector) using the connector id and connector name

        :param connection_name: Name of the connection to be created
        :param connector_id: Id of the connector
        :param override: Override connection if it already exists
        :return: Dictionary object returned by create connection call
        """
        ## Get Connection using connection name
        # connection_response = self._powerapps_rp.get_connection(
        #    connector_id=connector_id,
        #    connection_name=connection_name,
        #    environment_id=self._environment_name
        # )

        # If connection exists and needs to be updated
        # if connection_response and override:
        #    connection_request_body = PowerAppsCustomConnector._construct_connection_request_body(api_key=api_key)

        #    connection_response = self._powerapps_rp.update_connection(
        #        connector_id=connector_id,
        #        connection_name=connection_name,
        #        environment_id=self._environment_name,
        #        payload=connection_request_body
        #    )

        #    if connection_response is None:
        #        raise UpdateConnectionException("Connection update failed")

        # Connection doesn't exist, create a new connection
        # if connection_response is None:
        connection_request_body = PowerAppsCustomConnector. \
            _construct_connection_request_body(api_key=api_key, environment_object=environment_object)

        connection_response = self._powerapps_rp.create_connection(
            connector_id=connector_id,
            connection_name=connection_name,
            environment_id=self._environment_name,
            payload=connection_request_body
        )

        connection_statuses = connection_response[ccConstants.properties.value][ccConstants.statuses.value]
        if len(connection_statuses) and connection_statuses[0][ccConstants.status.value] == ccConstants.connected.value:
            if self._set_connection_permissions(connector_name=connector_name, connector_id=connector_id,
                                                connection_name=connection_name,
                                                org_url=org_url, cds_token=cds_token):
                return connection_response

        raise ConnectionCreationException("Connection creation failed")

    def _set_connection_permissions(self, connector_name: str, connector_id: str, connection_name: str, org_url: str,
                                    cds_token: str) -> bool:
        """
        Get service principal id from graph API and add it to access control lists

        :param connector_name: Name of the connector
        :param connection_name: Name of the connection
        :return: Returns True if update connection permissions call succeeds else returns False
        """

        graph_token = self._d365_connector.get_token_using_refresh_token(resource=_AccessConfig.GRAPH_RESOURCE.value)
        graph_client = _GraphClient(graph_token=graph_token)

        service_principal = graph_client.get_service_principal(application_id=GraphClientConstants.application_id.value)
        service_principal_id = graph_client.get_service_principal_id(service_principal=service_principal)

        self._powerapps_rp.update_connector_permissions(connector_name=connector_name,
                                                        service_principal_id=service_principal_id, org_url=org_url,
                                                        cds_token=cds_token)
        return self._powerapps_rp.update_connection_permissions(connector_id=connector_id,
                                                                connection_name=connection_name,
                                                                environment_id=self._environment_name,
                                                                service_principal_id=service_principal_id)

    @classmethod
    def create_connection(cls, environment_name: str, model_name: str, connection_name: str,
                          open_api_specification: _OpenAPISpecification, override: bool, org_url: str,
                          cds_token: str) -> dict:
        """
        Creates a custom connection using the open api specification passed

        :param environment_name: PowerApps environment id
        :param model_name: Name used for creating a connector
        :param connection_name: Name used for creating a connection
        :param open_api_specification: Validated open api specification
        :param override: Update connector and connection
        :return: Dictionary containing connection url, connection name, connector name and other details
        """

        # Create a swagger required by custom connector using the open api specification passed
        connector_swagger = CustomConnectorRequestBuilder(
            api_specification=open_api_specification,
            environment_name=environment_name,
            model_name=model_name).buildSwagger()

        # Creates an object of PowerApps custom connector class
        pa_custom_connector = PowerAppsCustomConnector(environment_name=environment_name)

        # Creates or retrieves a custom connector
        connector_response = pa_custom_connector._setup_connector(connector_swagger=connector_swagger,
                                                                  override=override)

        if not connector_response:
            raise Exception("Creation of connector failed")

        # Creates a connection on the above connector object
        connection_response = pa_custom_connector._setup_connection(
            connector_name=connector_response[ccConstants.properties.value].get("xrmConnectorId", ""),
            connection_name=connection_name,
            api_key=open_api_specification.get_primary_authentication_key(),
            connector_id=connector_response[ccConstants.id_key.value],
            environment_object=connector_response[ccConstants.properties.value][ccConstants.environment.value],
            override=override,
            org_url=org_url,
            cds_token=cds_token
        )

        if not connection_response:
            raise Exception("Creation of connection failed")

        # Returns a connector and connection details
        return PowerAppsCustomConnector._format_connection_response(
            connector_response=connector_response,
            connection_response=connection_response,
            open_api_specification=open_api_specification)

    @staticmethod
    def _format_connection_response(connector_response: dict, connection_response: dict,
                                    open_api_specification: _OpenAPISpecification) -> dict:
        """
        Creates a dictionary containing connector and connection details.

        :param connector_response: Create or retrieve connector response dictionary
        :param connection_response: Create connection response dictionary
        :param open_api_specification: Open API specification used to create a connector
        :return: Dictionary containing connector and connection details
        """
        connection_url = f"{connector_response['properties']['primaryRuntimeUrl'].strip('/')}/" \
            f"{connection_response['name'].strip('/')}/" \
            f"{open_api_specification.get_scoring_uri_path().strip('/')}"

        return {
            "connection_url": connection_url,
            "predictUrl": connection_url,
            "modelPredictUrl": open_api_specification._scoring_url,
            "ModelEndPointPath": open_api_specification.scoring_path,

            "connector_id": connector_response["id"],
            "connector_creation_time": connector_response["properties"]["createdTime"],
            "connector_changed_time": connector_response["properties"]["changedTime"],
            "connector_primary_runtime_url": connector_response["properties"]["primaryRuntimeUrl"],

            "connection_id": connection_response["id"],
            "connection_name": connection_response["name"],
            "connection_creation_time": connection_response["properties"]["createdTime"],
            "connection_last_modified": connection_response["properties"]["lastModifiedTime"],
            "connection_reference_logical_name":
                connection_response["properties"]["createdXrmConnectionReferenceLogicalName"]
        }
