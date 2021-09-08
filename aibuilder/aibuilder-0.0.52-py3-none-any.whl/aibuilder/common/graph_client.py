#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------


from typing import Optional

from urllib3.exceptions import HTTPError

from aibuilder.common.auth.constants import _AccessConfig, _AccessTokenResponseFields
from aibuilder.common.constants import OpenAPIConstants, GraphClientConstants
from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.common.paconnector.request_builder import _RequestBuilder


class _GraphClient:
    """
    Class to query Graph APIs

    """

    def __init__(self, graph_token: dict) -> None:
        """
        Graph client class initialization

        :param graph_token: Dictionary containing access token, refresh token, user id and other token properties
        """
        self._graph_token = graph_token
        self._request_builder = _RequestBuilder(
            url=_AccessConfig.GRAPH_RESOURCE.value,
            token=self._graph_token[_AccessTokenResponseFields.ACCESS_TOKEN.value],
            base_path=GraphClientConstants.graph_api_version.value)

    def get_service_principal(self, application_id: str) -> Optional[dict]:
        """
        Queries for service principal using application id and user context

        :param application_id: Application id for which service principal needs to be queried
        :return: Service principal dictionary containing id, name and other properties
        """
        filter_query = {
            OpenAPIConstants.filter.value:
                f"{GraphClientConstants.application_id_key.value} {OpenAPIConstants.equals.value} '{application_id}'"
        }

        endpoint = self._request_builder.construct_url(path=GraphClientConstants.service_principal_path.value,
                                                       query=filter_query)

        response = self._request_builder.request(method=RequestBuilderConstants.GET, endpoint=endpoint)

        if response.status_code == 200:
            results = response.json()
            if OpenAPIConstants.value.value in results and len(results[OpenAPIConstants.value.value]) > 0:
                return results[OpenAPIConstants.value.value][0] if results[OpenAPIConstants.value.value][0] else None
            raise ValueError(f"Service Principal Id not found for "
                             f"tenant id: {self._graph_token.get(_AccessTokenResponseFields.TENANT_ID.value)} and "
                             f"user id: {self._graph_token.get(_AccessTokenResponseFields.USER_ID.value)}")

        raise HTTPError(f"Get service principal returned response: {response}")

    @staticmethod
    def get_service_principal_id(service_principal: Optional[dict]) -> str:
        """
        Gets service principal id from service principal

        :param service_principal: Service principal dictionary containing id, name and other properties
        :return: Service principal id from service principal
        """
        if not service_principal:
            raise ValueError(f"Service principal is either None or empty: {service_principal}")

        service_principal_id = service_principal[OpenAPIConstants.object_id.value]
        return service_principal_id
