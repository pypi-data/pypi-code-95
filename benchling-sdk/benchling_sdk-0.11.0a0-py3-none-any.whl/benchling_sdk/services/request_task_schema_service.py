from typing import List, Optional, Union

from benchling_api_client.api.schemas import get_request_task_schema, list_request_task_schemas
from benchling_api_client.models.bad_request_error import BadRequestError
from benchling_api_client.models.request_task_schema import RequestTaskSchema
from benchling_api_client.models.request_task_schemas_paginated_list import RequestTaskSchemasPaginatedList
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.services.base_service import BaseService


class RequestTaskSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> RequestTaskSchema:
        response = get_request_task_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def request_task_schemas_page(
        self, *, next_token: Optional[str] = None, page_size: Optional[int] = 50
    ) -> Response[Union[RequestTaskSchemasPaginatedList, BadRequestError]]:
        return list_request_task_schemas.sync_detailed(
            client=self.client, next_token=none_as_unset(next_token), page_size=none_as_unset(page_size)
        )

    def list(self, *, page_size: Optional[int] = 50) -> PageIterator[RequestTaskSchema]:
        def api_call(
            next_token: NextToken,
        ) -> Response[Union[RequestTaskSchemasPaginatedList, BadRequestError]]:
            return self.request_task_schemas_page(next_token=next_token, page_size=page_size)

        def results_extractor(body: RequestTaskSchemasPaginatedList) -> Optional[List[RequestTaskSchema]]:
            return body.request_task_schemas

        return PageIterator(api_call, results_extractor)
