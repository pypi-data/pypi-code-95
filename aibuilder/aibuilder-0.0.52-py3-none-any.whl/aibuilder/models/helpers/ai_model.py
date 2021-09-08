#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from typing import Optional

import requests

from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.common.paconnector.exceptions import RequestFormatException
from aibuilder.models.helpers.constants import _AIModelConstants
from aibuilder.models.helpers.data_model_operator import DataModelOperator
from aibuilder.models.helpers.exceptions import RegistrationException
from aibuilder.models.helpers.utils import get_object_id


class AiModel(DataModelOperator):
    def __init__(self, url: str, token: str):
        """
        Class to perform CURD operations on AI Model

        :param url: PowerApps organization endpoint
        :param token: Bearer token used to authenticate with PowerApps
        """
        super().__init__(url, token)

    def create(self, model_name: str, template_id: str) -> str:
        """
        Creates AI Model on AI Builder

        :param model_name: Name of AI Model
        :param template_id: Template id to bind this AI Model
        :return: Returns model_id string
        """
        endpoint = self._request_builder.construct_url(_AIModelConstants.MSDYN_AIMODELS.value)
        payload = {
            _AIModelConstants.MSDYN_NAME.value: f"{model_name}",
            f"{_AIModelConstants.MSDYN_TEMPLATE_ID.value}@{_AIModelConstants.ODATA_BIND.value}":
                f"/{_AIModelConstants.MSDYN_TEMPLATES.value}({template_id})"
        }
        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return get_object_id(response.headers.get(_AIModelConstants.ODATA_ENTITY_ID.value))

    def retrieve(self, model_name: str) -> Optional[str]:
        filter_query = {
            _AIModelConstants.FILTER.value:
                f"{_AIModelConstants.MSDYN_NAME.value} {_AIModelConstants.EQUALS.value} '{model_name}'"
        }

        endpoint = self._request_builder.construct_url(_AIModelConstants.MSDYN_AIMODELS.value, query=filter_query)
        response = self._request_builder.request(RequestBuilderConstants.GET, endpoint)

        value = response.json().get(_AIModelConstants.VALUE.value)
        if isinstance(value, list) and len(value):
            return value[0][_AIModelConstants.MSDYN_AIMODEL_ID.value.lower()]
        return None

    def update(self, model_id: str) -> requests.Response:
        raise NotImplementedError

    def delete(self, model_name=None) -> requests.Response:
        raise NotImplementedError

    def schedule(self, model_id: str) -> requests.Response:
        """
        Set predict immediately to False for BYOM models
        :param model_id: AI Builder model id
        :return: Schedule call response
        """
        # Set schedule to Never
        url_path = f'{_AIModelConstants.MSDYN_AIMODELS.value}({model_id})/{_AIModelConstants.SCHEDULE_ACTION.value}'
        endpoint = self._request_builder.construct_url(url_path)
        payload = {
            _AIModelConstants.VERSION.value: _AIModelConstants.SCHEDULE_API_VERSION.value,
            _AIModelConstants.PREDICT_IMMEDIATELY.value: False
        }

        response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        return response

    def unschedule(self, model_id: str) -> bool:
        """
        Unschedule a model
        :param model_id: AI Builder model id
        :return: Status of unschedule action
        """
        url_path = f'{_AIModelConstants.MSDYN_AIMODELS.value}({model_id})/{_AIModelConstants.UNSCHEDULE_ACTION.value}'
        endpoint = self._request_builder.construct_url(url_path)
        payload = {
            _AIModelConstants.VERSION.value: _AIModelConstants.SCHEDULE_API_VERSION.value
        }

        try:
            response = self._request_builder.request(RequestBuilderConstants.POST, endpoint, payload=payload)
        except RequestFormatException as e:
            # if no model was found in published state, then return True
            return len(e.args) > 0 and "UnPublishedModel" in e.args[0]

        if response.status_code != 200:
            raise RegistrationException(f"Model unscheduling failed")

        return True
