from typing import List, Optional

from benchling_api_client.api.schemas import (
    get_location_schema,
    list_location_schemas,
    list_location_schemas_by_registry,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import LocationSchema, LocationSchemasPaginatedList, Schema
from benchling_sdk.services.base_service import BaseService


class LocationSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> Schema:
        response = get_location_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def location_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[LocationSchemasPaginatedList]:
        return list_location_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Schema]:
        def api_call(next_token: NextToken) -> Response[LocationSchemasPaginatedList]:
            return self.location_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: LocationSchemasPaginatedList) -> List[LocationSchema]:
            return body.location_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def list_by_registry(self, registry_id: str) -> List[Schema]:
        response = list_location_schemas_by_registry.sync_detailed(
            client=self.client, registry_id=registry_id
        )
        schema_list = model_from_detailed(response)
        return schema_list.location_schemas
