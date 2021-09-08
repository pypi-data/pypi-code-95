#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import logging
import json
from typing import Optional, Union
from urllib.parse import urljoin, urlunparse, urlparse

import requests
from azureml.core.webservice import Webservice
from azureml.exceptions import WebserviceException
from prance import ResolvingParser

from aibuilder.core.model_connection import ModelConnection, LocalFileConnection
from aibuilder.models.constants import OpenAPISpecificationConstants as api_constants
from aibuilder.models.constants import _AIBExecutionContextConstants
from aibuilder.models.exceptions import SchemaValidationException

logger = logging.getLogger(__name__)


class _OpenAPISpecification:
    def __init__(self, model_connection: [ModelConnection, Webservice]) -> None:
        """
        Open API Specification Builder class

        :param model_connection: Model connection object to retrieve open API swagger
        """
        self._request_label = None
        self._api_authentication_keys = None
        self._model_connection = model_connection
        if isinstance(model_connection, LocalFileConnection):
            self._specification, self._specification_version = \
                _OpenAPISpecification.get_api_specification_and_version(model_connection)
            self._scoring_url = self.get_scoring_url()
            self._request_label = self.get_request_label()
        elif isinstance(model_connection, Webservice):
            self._specification, self._specification_version = \
                _OpenAPISpecification.get_api_specification_and_version(model_connection,
                                                                        validate_host=False)
            self._scoring_url = model_connection.scoring_uri
            self._request_label = self.get_request_label()
            try:
                self._api_authentication_keys = model_connection.get_keys()
            except WebserviceException:
                self._api_authentication_keys = None
        else:
            raise RuntimeError(f"Model connection type is not supported: {model_connection}")

    @property
    def scoring_uri(self) -> str:
        """
        Returns API Scoring URI

        """
        return self._scoring_url

    @property
    def scoring_path(self) -> str:
        """
        Returns API scoring URI path

        """
        if isinstance(self._model_connection, Webservice):
            return f"/{self._scoring_url.split('/')[-1]}"
        return list(self._specification[api_constants.paths.value].keys())[0]

    @property
    def host(self) -> str:
        """
        Returns API Scoring URI host

        """
        return urlparse(self.scoring_uri).netloc

    @property
    def scheme(self) -> str:
        """
        Returns API Scoring URI scheme

        """
        return urlparse(self.scoring_uri).scheme

    @property
    def specification(self) -> dict:
        """
        Returns API Specification dictionary

        """
        return self._specification

    @property
    def specification_version(self) -> str:
        """
        Returns API Specification version

        """
        return self._specification_version

    def get_scoring_url(self) -> str:
        """
        Retrieves the scoring url from the api specification

        :return: Formatted scoring url
        """
        url_parts = [''] * 6

        url_parts[0] = self.specification[api_constants.schemes.value][0]
        url_parts[1] = self.specification[api_constants.host.value]

        base_path = self.specification[api_constants.base_path.value]
        path = list(self.specification[api_constants.paths.value].keys())[0]

        url_parts[2] = urljoin(base_path, path)

        return urlunparse(url_parts)

    def get_request_label(self) -> Optional[str]:
        """
        Extracts request body key from input specification to be used in constructing HTTP request

        :return: Request body key to be used in constructing HTTP request for calling model endpoint
        """
        input_properties = self.specification.get(api_constants.definitions.value, {}) \
            .get(api_constants.service_input.value, {}) \
            .get(api_constants.properties.value, {})
        input_property_keys = list(input_properties.keys())
        return input_property_keys[0] if input_property_keys else None

    def get_api_input_attributes(self) -> dict:
        """
        Extracts input attributes from API Specification dictionary

        :return: Dictionary containing input attributes information
        """
        input_attributes = self.specification.get(api_constants.definitions.value, {}) \
            .get(api_constants.service_input.value, {}) \
            .get(api_constants.properties.value, {}) \
            .get(self.get_request_label(), {}) \
            .get(api_constants.items.value, {}) \
            .get(api_constants.properties.value, {})

        return input_attributes

    def get_api_output_attributes(self) -> dict:
        """
        Extracts output API contract from API Specification dictionary

        :return: Dictionary containing output attributes information
        """
        output_attributes = self.specification.get(api_constants.definitions.value, {}) \
            .get(api_constants.service_output.value, {}) \
            .get(api_constants.items.value, {}) \
            .get(api_constants.properties.value, {})

        return output_attributes

    def get_output_attributes_with_aib_types(self) -> dict:
        output_attributes = self.get_api_output_attributes()
        for output_column in output_attributes:
            output_attributes[output_column]
        return output_attributes

    def get_scoring_config(self, prediction_timeout: Union[int, float], batch_size) -> dict:
        """
        Generates an scoring API config which can be used by a Http client

        :return: Dictionary containing scoring url, headers and method type information
        """
        return {
            _AIBExecutionContextConstants.predict_url.value: self._scoring_url,
            _AIBExecutionContextConstants.use_connectors.value: True,
            _AIBExecutionContextConstants.request_body_key.value: self._request_label,
            _AIBExecutionContextConstants.method.value: _AIBExecutionContextConstants.post.value,
            _AIBExecutionContextConstants.request_headers.value: {
                _AIBExecutionContextConstants.content_type.value: _AIBExecutionContextConstants.application_json.value
            },
            _AIBExecutionContextConstants.prediction_policy.value: {
                _AIBExecutionContextConstants.prediction_timeout.value: prediction_timeout,
                _AIBExecutionContextConstants.batch_size.value: batch_size
            }
        }

    def get_primary_authentication_key(self) -> Optional[str]:
        """
        Return primary authentication key

        :return: Primary authentication key if exists else returns None
        """
        if isinstance(self._api_authentication_keys, tuple):
            return self._api_authentication_keys[0]

    def get_scoring_uri_path(self) -> str:
        """
        Return scoring uri path

        :return: Returns scoring uri path if exists else returns empty string
        """
        if self._scoring_url:
            return urlparse(self._scoring_url).path
        return ""

    @staticmethod
    def get_api_specification_and_version(model_connection: ModelConnection, validate_host: bool = True) -> tuple:
        """
        Reads API Specification from file path and validates the API Specification

        :param model_connection: Model connection
        :param validate_host: Whether to validate scoring URI parts
        :return: Specification dictionary and specification version
        """
        try:
            # Reading swagger from URL or local location
            # TODO: Use ResolvingParser to read swagger when this bug is fixed.
            # https://github.com/RonnyPfannschmidt/prance/issues/88

            if isinstance(model_connection, Webservice):
                swagger = requests.get(model_connection.swagger_uri).text
            else:
                with open(model_connection.swagger_file_path, "r", encoding='utf-8') as f:
                    swagger_dict = json.load(f)
                    swagger = json.dumps(swagger_dict)

            parser = ResolvingParser(spec_string=swagger, backend='openapi-spec-validator')
            _OpenAPISpecification._validate_api_specification(parser.specification, parser.semver,
                                                              validate_host=validate_host)
            return parser.specification, parser.semver
        except Exception as ex:
            logger.info(f"{ex.args[0]}. Validation Error")
            raise SchemaValidationException(ex)

    @staticmethod
    def _validate_api_specification(api_specification: dict, api_specification_version: str,
                                    validate_host: bool = True) -> bool:
        """
        Validates if API specification object is as per AI Builder requirements

        :param api_specification: Dictionary containing Swagger API Specification
        :param api_specification_version: Swagger API Specification version
        :param validate_host: Whether to validate scoring URI parts
        :return: True if API specification is as per AI Builder requirements
        """
        if api_specification_version != '2.0.0':
            raise SchemaValidationException("Open API Specification Version must be 2.0.0")
        if api_constants.schemes.value not in api_specification:
            raise SchemaValidationException("Open API Specification must specify schemes")
        if api_constants.paths.value not in api_specification:
            raise SchemaValidationException("Open API Specification must specify paths")

        # Validates host and scoring URI parts required to construct a URI
        if validate_host:
            if api_constants.host.value not in api_specification:
                raise SchemaValidationException("Open API Specification must specify host")
            if api_constants.base_path.value not in api_specification:
                raise SchemaValidationException("Open API Specification must specify url base path")
            if len(api_specification[api_constants.paths.value]) != 1:
                raise SchemaValidationException("Open API Specification must have only one path")
        else:
            if len(api_specification[api_constants.paths.value]) == 0:
                raise SchemaValidationException("Open API Specification must have at least one path")

        return True
