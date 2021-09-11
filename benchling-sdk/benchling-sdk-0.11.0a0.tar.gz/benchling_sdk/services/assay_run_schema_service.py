from typing import List, Optional

from benchling_api_client.api.schemas import get_run_schema, list_assay_run_schemas
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import AssayRunSchema, AssayRunSchemasPaginatedList
from benchling_sdk.services.base_service import BaseService


class AssayRunSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> AssayRunSchema:
        response = get_run_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def run_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[AssayRunSchemasPaginatedList]:
        return list_assay_run_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[AssayRunSchema]:
        def api_call(next_token: NextToken) -> Response[AssayRunSchemasPaginatedList]:
            return self.run_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def runs_extractor(body: AssayRunSchemasPaginatedList) -> Optional[List[AssayRunSchema]]:
            return body.assay_run_schemas

        return PageIterator(api_call, runs_extractor)
