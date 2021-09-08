#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from typing import Optional

import requests

from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.models.aib_binding import AIBBinding
from aibuilder.models.constants import _AIBModelType
from aibuilder.models.helpers.constants import _AIModelConstants
from aibuilder.models.helpers.data_model_operator import DataModelOperator
from aibuilder.models.helpers.exceptions import RunConfigException
from aibuilder.models.helpers.utils import get_object_id, get_model_config_and_data_binding


class RunConfiguration(DataModelOperator):
    def __init__(self, url: str, token: str):
        """
        Class to perform CURD operations on Run Configuration

        :param url: PowerApps organization endpoint
        :param token: Bearer token used to authenticate with PowerApps
        """
        super().__init__(url, token)

    def create(self, model_type: _AIBModelType, model_name: str, model_id: str, train_config_id: str,
               scoring_config: dict, data_binding: Optional[AIBBinding], data_specification: str = "",
               batch_size: Optional[int] = None) -> str:
        """
        Creates a run configuration

        :param model_type: ML model type represented by ModelType enum
        :param model_name: Friendly Name of the ML model used to register with AI Builder
        :param model_id: New AI Configuration will be linked to this AI Model ID
        :param train_config_id: Train configuration ID
        :param scoring_config: Scoring configuration to be saved on AI Configuration
        :param data_binding: Data binding object to be saved on AI Configuration
        :param data_specification: Model run data specification to be saved on AI Run Configuration
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return: Run config id
        """
        endpoint = self._request_builder.construct_url(_AIModelConstants.MSDYN_AICONFIGURATIONS.value)
        connection_reference_id = self._get_connection_reference_id(
            connection_reference_logical_name=scoring_config["connection_reference_logical_name"])
        payload = RunConfiguration._create_payload(model_name, model_id, model_type, train_config_id,
                                                   connection_reference_id, scoring_config,
                                                   data_binding, data_specification, batch_size)
        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return get_object_id(response.headers.get('OData-EntityId'))

    def update(self, run_config_id: str) -> requests.Response:
        """
        Updates a AI Configuration to publish state

        :param run_config_id: Run config id of model
        :return: Response from update call
        """
        # publish the model
        url_path = f'{_AIModelConstants.MSDYN_AICONFIGURATIONS.value}' \
            f'({run_config_id})/{_AIModelConstants.PUBLISH_ACTION.value}'
        endpoint = self._request_builder.construct_url(url_path)
        payload = {f"{_AIModelConstants.VERSION.value}": f"{_AIModelConstants.UPDATE_API_VERSION.value}"}

        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return response

    def _get_connection_reference_id(self, connection_reference_logical_name: str) -> str:
        """
        Get connection reference id by filtering connection reference table on connection reference logical name
        :param connection_reference_logical_name: Connection reference logical name
        :return: connection reference id
        """
        # get connection reference
        url_path = _AIModelConstants.CONNECTION_REFERENCES.value
        query = {
            _AIModelConstants.FILTER.value:
                f"{_AIModelConstants.CONNECTION_REFERENCE_LOGICAL_NAME.value} eq '{connection_reference_logical_name}'"
        }
        endpoint = self._request_builder.construct_url(url_path, query=query)
        response = self._request_builder.request(RequestBuilderConstants.GET, endpoint)

        if response.status_code == 200:
            response_dict = response.json()[_AIModelConstants.VALUE.value][0]
            return response_dict.get(_AIModelConstants.CONNECTION_REFERENCE_ID.value)

        raise ValueError(f"Connection reference filter query failed. "
                         f"Response: {response.status_code} - {response.text}")

    @staticmethod
    def _create_payload(model_name: str, model_id: str, model_type: _AIBModelType, train_config_id: str,
                        connection_reference_id: str,
                        scoring_config: dict, data_binding: Optional[AIBBinding],
                        data_specification: Optional[str] = "", batch_size: Optional[int] = None) -> dict:
        """
        Creates the request payload for train config

        :param model_name: Friendly Name of the ML model used to register with AI Builder
        :param model_id: New AI Configuration will be linked to this AI Model ID
        :param model_type: ML model type represented by ModelType enum
        :param train_config_id: Train Configuration ID
        :param connection_reference_id: Connection reference ID
        :param scoring_config: Scoring configuration to be saved on AI Configuration
        :param data_binding: Data binding object to be saved on AI Run Configuration
        :param data_binding: Data binding object to be saved on AI Run Configuration
        :param data_specification: Model run data specification to be saved on AI Run Configuration
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return: Payload to be used in calling create Train AI Configuration
        """
        data_binding, custom_config = get_model_config_and_data_binding(
            model_type, scoring_config, data_binding, batch_size, data_specification=data_specification,
            config_type=_AIModelConstants.RUN_CONFIG_TYPE)
        payload = {
            f"{_AIModelConstants.MSDYN_NAME.value}": f"{model_name} Run Config",
            f"{_AIModelConstants.MSDYN_AIMODEL_ID.value}@{_AIModelConstants.ODATA_BIND.value}":
                f"/{_AIModelConstants.MSDYN_AIMODELS.value}({model_id})",
            f"{_AIModelConstants.MSDYN_TYPE.value}": _AIModelConstants.RUN_CONFIG_TYPE.value,
            f"{_AIModelConstants.MSDYN_DATA_BINDING.value}": data_binding,
            f"{_AIModelConstants.MSDYN_CUSTOM_CONFIGURATION.value}": custom_config,
            f"{_AIModelConstants.MSDYN_RUN_CONFIG_ID.value}@{_AIModelConstants.ODATA_BIND.value}":
                f"/{_AIModelConstants.MSDYN_AICONFIGURATIONS.value}({train_config_id})",
            f"{_AIModelConstants.MSDYN_CONNECTION_REFERENCE_ID.value}@{_AIModelConstants.ODATA_BIND.value}":
                f"/{_AIModelConstants.CONNECTION_REFERENCES.value}({connection_reference_id})",
            "msdyn_schedulingoptions": "{\"schemaVersion\":2,\"prediction\":{\"recurrence\":{\"frequency\":\"Never\"}}}"
        }
        return payload

    def delete(self):
        raise NotImplementedError

    def predict(self, model_id, payload):
        raise NotImplementedError

    def retrieve(self, run_config_id: str) -> dict:
        """
        Retrieve run configuration based on run configuration id
        :param run_config_id: Run configuration id
        :return: Run configuration dictionary
        """
        url_path = f'{_AIModelConstants.MSDYN_AICONFIGURATIONS.value}({run_config_id})'
        endpoint = self._request_builder.construct_url(url_path)

        response = self._request_builder.request(RequestBuilderConstants.GET, endpoint)

        if response.status_code != 200:
            raise RunConfigException(f"Could not find run config {run_config_id}. Response: {response}")

        return response.json()
