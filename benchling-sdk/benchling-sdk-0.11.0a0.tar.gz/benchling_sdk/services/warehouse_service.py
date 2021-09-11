from benchling_api_client.api.warehouse import create_warehouse_credentials
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.models import WarehouseCredentials, WarehouseCredentialsCreate
from benchling_sdk.services.base_service import BaseService


class WarehouseService(BaseService):
    @api_method
    def create_credentials(self, credentials: WarehouseCredentialsCreate) -> WarehouseCredentials:
        response = create_warehouse_credentials.sync_detailed(client=self.client, json_body=credentials)
        return model_from_detailed(response)
