#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from urllib.parse import urlparse, urlunparse

from aibuilder.common.paconnector.constants import CustomConnectorConstants as ccConstants
from aibuilder.models.open_api_specification import _OpenAPISpecification


class CustomConnectorRequestBuilder:
    def __init__(self, api_specification: _OpenAPISpecification, environment_name: str = "", model_name: str = ""):
        """
        Building the swagger for a custom connector
        :param api_specification: _OpenAPISpecification object describing the API
        :param environment_name: PowerApps environment name (non-friendly)
        :param model_name: Model name that will be registered to PowerApps
        """
        self._api_specification = api_specification
        self.aci_service_primary_key = api_specification.get_primary_authentication_key()
        self.scoring_uri = api_specification.scoring_uri
        self.environment_name = environment_name
        self._swagger = api_specification.specification
        self.model_name = model_name
        self.properties = {}

        self._swagger.pop("host", None)
        self._api_base_path = self._swagger.pop("basePath", "/")
        self._swagger["schemes"] = [self._api_specification.scheme]

        paths = self._swagger['paths']
        self._swagger['paths'] = {self._api_specification.scoring_path: paths[self._api_specification.scoring_path]}

        self._swagger["host"] = self._api_specification.host
        self._swagger["basePath"] = self._api_base_path

    def description(self) -> dict:
        """
        Gets the description from ACI service swagger and adds it to the connector swagger
        :return: swagger description
        """
        return {ccConstants.description.value: self._swagger['info']['description']}

    def openApiDefinition(self) -> dict:
        """
        Gets the Open API Specification from the service swagger
        :return: dictionary containing the Open API Specification
        """
        return {ccConstants.openApiDefinition.value: self._swagger}

    def policyTemplateInstances(self) -> dict:
        """
        Sets the policy template instance for the connector
        :return: dictionary of list of policies
        """
        auth_parameters = None
        if self.aci_service_primary_key:
            auth_parameters = [{
                "title": "SetHeader",
                "templateId": "setheader",
                "parameters": {
                    "x-ms-apimTemplateParameter.name": "Authorization",
                    "x-ms-apimTemplateParameter.value": f"Bearer {self.aci_service_primary_key}",
                    "x-ms-apimTemplateParameter.existsAction": "override",
                    "x-ms-apimTemplate-policySection": "Request",
                    "x-ms-apimTemplate-operationName": [
                        self._swagger['paths'][self._api_specification.scoring_path]['post']['operationId']]
                }
            }]
        return {
            ccConstants.policyTemplateInstances.value: auth_parameters
        }

    def backendService(self) -> dict:
        """
        Gets the backend service endpoint
        :return: dictionary containing the service endpoint
        """
        service_url_parsed = urlparse(self.scoring_uri)
        service_url = urlunparse(service_url_parsed._replace(path=self._api_base_path))
        return {ccConstants.backendService.value: {"serviceUrl": service_url}}

    def environment(self) -> dict:
        """
        Gets the environment name (non-friendly)
        :return: dictionary containing the environment name
        """
        return {ccConstants.environment.value: {"name": self.environment_name}}

    def displayName(self) -> dict:
        """
        Sets the model name for the connector which would be used to register the model to PowerApps
        :return: display name
        """
        return {ccConstants.displayName.value: self.model_name}

    def connectionParameters(self) -> dict:
        """
        Sets the connection parameters based on the security definitions in the service swagger
        :return: dictionary of the connection parameters
        """
        connection_parameters = None
        if self.aci_service_primary_key:
            connection_parameters = {
                self._swagger['securityDefinitions']["Bearer"]["type"]: {
                    "type": "securestring",
                    "uiDefinition": {
                        "displayName": "API Key",
                        "description": "The API Key for this api",
                        "tooltip": "Provide your API Key",
                        "constraints": {
                            "tabIndex": 2,
                            "clearText": False,
                            "required": "true"
                        }
                    }
                }
            }
        return {
            ccConstants.connectionParameters.value: connection_parameters
        }

    def buildSwagger(self) -> dict:
        """
        Builds the swagger needed for the PowerApps custom connector
        :return: dictionary containing the properties needed for the swagger
        """
        self.properties.update(self.description())
        self.properties.update(self.openApiDefinition())
        self.properties.update(self.policyTemplateInstances())
        self.properties.update(self.backendService())
        self.properties.update(self.environment())
        self.properties.update(self.displayName())
        self.properties.update(self.connectionParameters())
        self.properties.update({ccConstants.capabilities.value: []})
        return {ccConstants.properties.value: self.properties}
