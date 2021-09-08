#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from enum import Enum


class PowerAppsSettings(Enum):
    """PowerApps connector constants"""
    PROD_URL = "https://api.powerapps.com"
    TIP_URL = "https://tip1.api.powerapps.com"
    INSTANCE_URL = 'instanceUrl'
    API_VERSION = "2017-06-01"
    BASE_PATH = "providers/Microsoft.PowerApps"
    PROPERTIES = 'properties'
    LINKED_ENVIRONMENT_METADATA = 'linkedEnvironmentMetadata'
    FRIENDLY_NAME = 'friendlyName'
    ENVIRONMENTS = "environments"
    IsPaiEnabled = "IsPaiEnabled"


class RequestBuilderConstants(Enum):
    """Constants used in Request Builder class"""
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"


class PowerAppsApiSettings(Enum):
    """PowerApps API Settings"""
    BASE_URL = "api/data/v9.0"
    TEMPLATES = 'templates'
    BYOM = 'BringYourOwnModel'


class CustomConnectorConstants(Enum):
    properties = "properties"
    description = "description"
    backendService = "backendService"
    connectionParameters = "connectionParameters"
    openApiDefinition = "openApiDefinition"
    policyTemplateInstances = "policyTemplateInstances"
    displayName = "displayName"
    environment = "environment"
    capabilities = "capabilities"
    name = "name"
    token = "token"

    # Connector specific constants
    connector_id = 'connectorId'

    # Connection specific constants
    connections = "connections"
    api_key = "apiKey"
    connection_parameters = "connectionParameters"
    status = "status"
    statuses = "statuses"
    connected = "Connected"
    id_key = "id"
    primary_runtime_url = "primaryRuntimeUrl"
    create_connection_reference = "createConnectionReference"
    solution_id = "solutionId"
    default_solution_id = "fd140aaf-4df4-11dd-bd17-0019b9312238"

    # PowerApps RP settings
    powerapps_url = 'powerAppsUrl'
    powerapps_api_version = 'powerAppsApiVersion'
    powerapps_base_path = 'base_path'


class ConnectionPermissionsConstants(Enum):
    modify_permissions = "modifyPermissions"
    put = "put"
    properties = "properties"
    role_name = "roleName"
    can_view_with_share = "CanViewWithShare"
    capabilites = "capabilities"
    principal = "principal"
    permissions_id = "id"
    permissions_type = "type"
    service_principal = "ServicePrincipal"
    tenant_id = "tenantId"
    delete = "delete"
