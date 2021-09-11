from typing import Iterable, List

from benchling_api_client.api.inventory import validate_barcodes
from benchling_api_client.client import Client
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.models import BarcodesList, BarcodeValidationResult
from benchling_sdk.services.base_service import BaseService


class InventoryService(BaseService):
    def __init__(
        self,
        client: Client,
        retry_strategy: RetryStrategy,
    ):
        super().__init__(client, retry_strategy)

    @api_method
    def validate_barcodes(self, registry_id: str, barcodes: Iterable[str]) -> List[BarcodeValidationResult]:
        barcodes_list = BarcodesList(barcodes=list(barcodes))
        response = validate_barcodes.sync_detailed(
            client=self.client, registry_id=registry_id, json_body=barcodes_list
        )
        results = model_from_detailed(response)
        return results.validation_results
