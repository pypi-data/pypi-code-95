from typing import List, Optional

from benchling_api_client.api.schemas import (
    get_batch_schema,
    list_batch_schemas,
    list_batch_schemas_by_registry,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import BatchSchema, BatchSchemasPaginatedList
from benchling_sdk.services.base_service import BaseService


class BatchSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> BatchSchema:
        response = get_batch_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def batch_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[BatchSchemasPaginatedList]:
        return list_batch_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[BatchSchema]:
        def api_call(next_token: NextToken) -> Response[BatchSchemasPaginatedList]:
            return self.batch_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: BatchSchemasPaginatedList) -> Optional[List[BatchSchema]]:
            return body.batch_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def list_by_registry(self, registry_id: str) -> List[BatchSchema]:
        response = list_batch_schemas_by_registry.sync_detailed(client=self.client, registry_id=registry_id)
        schema_list = model_from_detailed(response)
        return schema_list.batch_schemas
