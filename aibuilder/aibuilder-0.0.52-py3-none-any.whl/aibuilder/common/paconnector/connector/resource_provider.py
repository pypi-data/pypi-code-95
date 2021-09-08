#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from typing import Optional
from urllib.parse import urljoin

from requests.exceptions import HTTPError

from aibuilder.common.paconnector.constants import ConnectionPermissionsConstants
from aibuilder.common.paconnector.constants import CustomConnectorConstants as ccConstants
from aibuilder.common.paconnector.constants import PowerAppsApiSettings, PowerAppsSettings
from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.common.paconnector.request_builder import _RequestBuilder


class PowerAppsRP:
    def __init__(self, api_manager: _RequestBuilder):
        self.api_manager = api_manager

    def get_connector(self, environment: str, connector_id: str) -> Optional[dict]:
        """
        Returns API registration JSON for a given connector.
        :param environment: Non friendly environment name string
        :param connector_id: Connector ID
        :return:
        """
        if connector_id is None:
            return None

        api = urljoin('apis/', connector_id)

        endpoint = self.api_manager.construct_url(
            path=api,
            query=PowerAppsRP._get_filter_query(environment))

        response = self.api_manager.request(
            method=RequestBuilderConstants.GET,
            endpoint=endpoint)

        return response.json()

    def create_connector(self, environment: str, payload: dict) -> dict:
        """
        Creates a new custom connector.
        :param environment: Non friendly environment name string
        :param payload: dictionary containing the payload
        :return:
        """
        endpoint = self.api_manager.construct_url(
            path='apis',
            query=PowerAppsRP._get_filter_query(environment, use_default_solution_id=True))

        response = self.api_manager.request(
            method=RequestBuilderConstants.POST,
            endpoint=endpoint,
            payload=payload)

        return response.json()

    def update_connector(self, environment: str, connector_id: str, payload: dict) -> bool:
        """
        Updates a custom connector.
        :param environment: Non friendly environment name string
        :param connector_id: Connector ID
        :param payload: dictionary containing the payload
        :return:
        """
        api = urljoin('apis/', connector_id)

        endpoint = self.api_manager.construct_url(
            path=api,
            query=PowerAppsRP._get_filter_query(environment))

        response = self.api_manager.request(
            method=RequestBuilderConstants.PATCH,
            endpoint=endpoint,
            payload=payload)

        return response.status_code == 204

    def get_all_connectors(self, environment: str) -> dict:
        """
        Returns all connectors.
        :param environment: Non friendly environment name string
        :return:
        """
        endpoint = self.api_manager.construct_url(
            path='apis',
            query=PowerAppsRP._get_filter_query(environment))

        response = self.api_manager.request(
            method=RequestBuilderConstants.GET,
            endpoint=endpoint)

        return response.json()

    def validate_connector(self, payload, enable_certification_rules) -> dict:
        """
        Validates a custom connector.
        """
        api = self.api_manager.add_object_id('validateApiSwagger')

        query = None
        if enable_certification_rules:
            query = {'enableConnectorCertificationRules': 'true'}

        endpoint = self.api_manager.construct_url(
            path=api,
            query=query)

        response = self.api_manager.request(
            method=RequestBuilderConstants.POST,
            endpoint=endpoint,
            payload=payload)

        return response.json()

    def get_connection(self, connector_id: str, connection_name: str, environment_id: str) -> Optional[dict]:
        """
        Get connection using the connector id and connection name.

        :param connector_id: Connector id on which a connection needs to be created
        :param connection_name: Name of the connection
        :param environment_id: PowerApps environment id where a connection will be created
        :return: Request response text
        """
        endpoint = self._construct_connection_endpoint(connector_id=connector_id, connection_name=connection_name,
                                                       environment_id=environment_id)

        try:
            response = self.api_manager.request(
                method=RequestBuilderConstants.GET,
                endpoint=endpoint)
        except HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise e

        return response.json()

    def create_connection(self, connector_id: str, connection_name: str, environment_id: str, payload: dict) -> dict:
        """
        Creates a new connection using the connector id and payload.

        :param connector_id: Connector id on which a connection needs to be created
        :param connection_name: Name of the connection
        :param environment_id: PowerApps environment id where a connection will be created
        :param payload: Dictionary containing connection information
        :return: Request response text
        """
        endpoint = self._construct_connection_endpoint(connector_id=connector_id, connection_name=connection_name,
                                                       environment_id=environment_id, create_connection_reference=True)

        response = self.api_manager.request(
            method=RequestBuilderConstants.PUT,
            endpoint=endpoint,
            payload=payload)

        return response.json()

    def update_connection(self, connector_id: str, connection_name: str, environment_id: str, payload: dict) -> dict:
        """
        Creates a new connection using the connector id and payload.

        :param connector_id: Connector id associated with the connection
        :param connection_name: Name of the connection that has to be updated
        :param environment_id: PowerApps environment id where a connection is created
        :param payload: Dictionary containing connection information
        :return: Request response text
        """
        endpoint = self._construct_connection_endpoint(connector_id=connector_id, connection_name=connection_name,
                                                       environment_id=environment_id)

        response = self.api_manager.request(
            method=RequestBuilderConstants.PATCH,
            endpoint=endpoint,
            payload=payload)

        return response.json()

    def update_connection_permissions(self, connector_id: str, connection_name: str, environment_id: str,
                                      service_principal_id: str) -> bool:
        """
        Adds service principal id of the app to access control lists

        :param connector_id: Id of the connector
        :param connection_name: Name of the connection
        :param environment_id: PowerApps environment id where a connection is created
        :param service_principal_id: Service Principal that needs access to the connection
        :return: Returns True if update connection permissions call succeeds else returns False
        """
        permissions_endpoint = self._construct_connection_endpoint(
            connector_id=connector_id, connection_name=connection_name, environment_id=environment_id,
            extra_path=ConnectionPermissionsConstants.modify_permissions.value, use_default_solution_id=True)

        payload = {
            ConnectionPermissionsConstants.put.value: [
                {
                    ConnectionPermissionsConstants.properties.value: {
                        ConnectionPermissionsConstants.role_name.value:
                            ConnectionPermissionsConstants.can_view_with_share.value,
                        ConnectionPermissionsConstants.capabilites.value: [],
                        ConnectionPermissionsConstants.principal.value: {
                            ConnectionPermissionsConstants.permissions_id.value: service_principal_id,
                            ConnectionPermissionsConstants.permissions_type.value:
                                ConnectionPermissionsConstants.service_principal.value,
                            ConnectionPermissionsConstants.tenant_id.value: None
                        }
                    }
                }
            ],
            ConnectionPermissionsConstants.delete.value: []
        }

        response = self.api_manager.request(
            method=RequestBuilderConstants.POST,
            endpoint=permissions_endpoint,
            payload=payload)

        return response.status_code == 200

    def update_connector_permissions(self, connector_name: str, service_principal_id: str, org_url: str,
                                     cds_token: str) -> bool:
        """
        Grand application user permissions to the connector

        :param connector_id: Id of the connector
        :param service_principal_id: Service Principal that needs access to the connection
        :return: Returns True if update connection permissions call succeeds else returns False
        """
        base_path = PowerAppsApiSettings.BASE_URL.value
        request_builder = _RequestBuilder(url=org_url, base_path=base_path, token=cds_token)
        permissions_endpoint = request_builder.construct_url(path="GrantAccess")

        payload = {
            "Target": {
                "@odata.type": "Microsoft.Dynamics.CRM.connector",
                "connectorid": connector_name
            },
            "PrincipalAccess": {
                "Principal": {
                    "@odata.type": "Microsoft.Dynamics.CRM.systemuser",
                    "ownerid": service_principal_id
                },
                "AccessMask": "ReadAccess"
            }
        }

        response = request_builder.request(
            method=RequestBuilderConstants.POST,
            endpoint=permissions_endpoint,
            payload=payload)

        return response.status_code == 204

    def _construct_connection_endpoint(self, connector_id: str, connection_name: str, environment_id: str,
                                       extra_path: str = "", use_default_solution_id: bool = False,
                                       create_connection_reference: bool = False) -> str:
        """
        Construct connection endpoint using connector id, connection name, environment id and other parameters

        :param connector_id: Id of an existing connector
        :param connection_name: Name of the connection
        :param environment_id: PowerApps environment id where connector is created
        :param extra_path: Add extra path to API url
        :param use_default_solution_id: Boolean to add default solution id to query parameter
        :param create_connection_reference: Boolean to set create connection reference in query parameter
        :return: URL endpoint constructed using input parameters
        """
        if not (connector_id and connection_name and environment_id):
            raise ValueError("Connector id, connection name and environment id values cannot be None or empty string")

        api = f"{connector_id}/{ccConstants.connections.value}/{connection_name}"
        if extra_path:
            api = f"{api}/{extra_path}"

        endpoint = self.api_manager.construct_url(
            path=api,
            query=PowerAppsRP._get_filter_query(environment_id, use_default_solution_id=use_default_solution_id,
                                                create_connection_reference=create_connection_reference))

        return endpoint

    @staticmethod
    def _get_filter_query(environment_id: str, use_default_solution_id: bool = False,
                          create_connection_reference: bool = False) -> dict:
        """
        Construct a filter query dictionary
        :param environment_id: Id of the environment being used
        :param use_default_solution_id: Boolean to add default solution id to filter query
        :param create_connection_reference: Boolean to set create connection reference in filter query
        :return: Filter query dictionary
        """

        query = {'$filter': f"{ccConstants.environment.value} eq '{environment_id}'"}

        if use_default_solution_id:
            query.update({ccConstants.solution_id.value: ccConstants.default_solution_id.value})

        if create_connection_reference:
            query.update({ccConstants.create_connection_reference.value: True})

        return query

    @staticmethod
    def get_from_settings(settings: dict):
        """
        Returns PowerApps RP object from a given settings and credentials.
        """
        powerapps_api_manager = _RequestBuilder(
            url=settings[ccConstants.powerapps_url.value],
            base_path=settings[ccConstants.powerapps_base_path.value],
            api_version=settings[ccConstants.powerapps_api_version.value],
            token=settings[ccConstants.token.value])

        powerapps_rp = PowerAppsRP(api_manager=powerapps_api_manager)
        return powerapps_rp
