from typing import List, Optional

from benchling_api_client.api.schemas import (
    get_entity_schema,
    list_entity_schemas,
    list_entity_schemas_by_registry,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import EntitySchema, EntitySchemasPaginatedList
from benchling_sdk.services.base_service import BaseService


class EntitySchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> EntitySchema:
        response = get_entity_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def entity_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[EntitySchemasPaginatedList]:
        return list_entity_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[EntitySchema]:
        def api_call(next_token: NextToken) -> Response[EntitySchemasPaginatedList]:
            return self.entity_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: EntitySchemasPaginatedList) -> Optional[List[EntitySchema]]:
            return body.entity_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def list_by_registry(self, registry_id: str) -> List[EntitySchema]:
        response = list_entity_schemas_by_registry.sync_detailed(client=self.client, registry_id=registry_id)
        schema_list = model_from_detailed(response)
        return schema_list.entity_schemas
