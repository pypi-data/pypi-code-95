from typing import List, Optional

from benchling_api_client.api.schemas import (
    get_plate_schema,
    list_plate_schemas,
    list_plate_schemas_by_registry,
)
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import PlateSchema, PlateSchemasPaginatedList
from benchling_sdk.services.base_service import BaseService


class PlateSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> PlateSchema:
        response = get_plate_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def plate_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[PlateSchemasPaginatedList]:
        return list_plate_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[PlateSchema]:
        def api_call(next_token: NextToken) -> Response[PlateSchemasPaginatedList]:
            return self.plate_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: PlateSchemasPaginatedList) -> Optional[List[PlateSchema]]:
            # TODO BNCH-20802 The code generated type is incorrect
            return body.plate_schemas  # type: ignore

        return PageIterator(api_call, results_extractor)

    @api_method
    def list_by_registry(self, registry_id: str) -> List[PlateSchema]:
        response = list_plate_schemas_by_registry.sync_detailed(client=self.client, registry_id=registry_id)
        schema_list = model_from_detailed(response)
        return schema_list.plate_schemas
