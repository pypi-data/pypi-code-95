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
from aibuilder.models.helpers.exceptions import TrainConfigException
from aibuilder.models.helpers.utils import get_object_id, get_model_config_and_data_binding


class TrainConfiguration(DataModelOperator):
    def __init__(self, url: str, token: str):
        """
        Class to perform CURD operations on Train Configuration

        :param url: PowerApps organization endpoint
        :param token: Bearer token used to authenticate with PowerApps
        """
        super().__init__(url, token)

    def create(self, model_type: _AIBModelType, model_name: str, model_id: str, scoring_config: dict,
               data_binding: Optional[AIBBinding], batch_size: Optional[int] = None) -> str:
        """
        Creates an ai configuration (run or train)

        :param model_type: ML model type represented by ModelType enum
        :param model_name: Friendly Name of the ML model used to register with AI Builder
        :param model_id: New AI Configuration will be linked to this AI Model ID
        :param scoring_config: Scoring configuration to be saved on AI Configuration
        :param data_binding: Data binding object to be saved on AI Configuration
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return: Train config id
        """
        endpoint = self._request_builder.construct_url(_AIModelConstants.MSDYN_AICONFIGURATIONS.value)
        payload = TrainConfiguration._create_payload(model_name, model_id, model_type, scoring_config, data_binding,
                                                     batch_size)
        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return get_object_id(response.headers.get('OData-EntityId'))

    def update(self, train_config_id: str) -> requests.Response:
        """
        Updates a AI Configuration to trained state

        :param train_config_id: Train config id of model
        :return: Response from update call
        """
        url_path = _AIModelConstants.MSDYN_AICONFIGURATIONS.value + \
            f'({train_config_id})/{_AIModelConstants.TRAIN_ACTION.value}'
        endpoint = self._request_builder.construct_url(url_path)
        payload = {f"{_AIModelConstants.VERSION.value}": f"{_AIModelConstants.UPDATE_API_VERSION.value}"}

        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return response

    @staticmethod
    def _create_payload(model_name: str, model_id: str, model_type: _AIBModelType, scoring_config: dict,
                        data_binding: Optional[AIBBinding], batch_size: Optional[int] = None) -> dict:
        """
        Creates the request payload for train config

        :param model_name: Friendly Name of the ML model used to register with AI Builder
        :param model_id: New AI Configuration will be linked to this AI Model ID
        :param model_type: ML model type represented by ModelType enum
        :param scoring_config: Scoring configuration to be saved on AI Configuration
        :param data_binding: Data binding object to be saved on AI Configuration
        :param batch_size: Number of prediction rows model endpoint can handle in one call
        :return: Payload to be used in calling create Train AI Configuration
        """
        data_binding, custom_config = get_model_config_and_data_binding(model_type, scoring_config,
                                                                        data_binding, batch_size)
        payload = {
            f"{_AIModelConstants.MSDYN_NAME.value}": f"{model_name} Train Config",
            f"{_AIModelConstants.MSDYN_AIMODEL_ID.value}@{_AIModelConstants.ODATA_BIND.value}":
                f"/{_AIModelConstants.MSDYN_AIMODELS.value}({model_id})",
            f"{_AIModelConstants.MSDYN_TYPE.value}": _AIModelConstants.TRAIN_CONFIG_TYPE.value,
            f"{_AIModelConstants.MSDYN_CUSTOM_CONFIGURATION.value}": custom_config
        }
        return payload

    def retrieve(self, train_config_id: str) -> dict:
        """
        Retrieve train configuration based on train configuration id
        :param train_config_id: Train configuration id
        :return: Train configuration dictionary
        """
        url_path = f'{_AIModelConstants.MSDYN_AICONFIGURATIONS.value}({train_config_id})'
        endpoint = self._request_builder.construct_url(url_path)

        response = self._request_builder.request(RequestBuilderConstants.GET, endpoint)

        if response.status_code != 200:
            raise TrainConfigException(f"Could not find train config {train_config_id}. Response: {response}")

        return response.json()

    def delete(self):
        raise NotImplementedError
