from typing import List, Optional

from benchling_api_client.api.schemas import get_result_schema, list_assay_result_schemas
from benchling_api_client.types import Response
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import AssayResultSchema, AssayResultSchemasPaginatedList
from benchling_sdk.services.base_service import BaseService


class AssayResultSchemaService(BaseService):
    @api_method
    def get_by_id(self, schema_id: str) -> AssayResultSchema:
        response = get_result_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def result_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[AssayResultSchemasPaginatedList]:
        return list_assay_result_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[AssayResultSchema]:
        def api_call(next_token: NextToken) -> Response[AssayResultSchemasPaginatedList]:
            return self.result_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: AssayResultSchemasPaginatedList) -> Optional[List[AssayResultSchema]]:
            return body.assay_result_schemas

        return PageIterator(api_call, results_extractor)
