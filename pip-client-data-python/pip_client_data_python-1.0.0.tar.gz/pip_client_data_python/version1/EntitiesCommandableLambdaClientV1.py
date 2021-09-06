# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_aws.clients.CommandableLambdaClient import CommandableLambdaClient
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import FilterParams, PagingParams, DataPage

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesCommandableLambdaClientV1(CommandableLambdaClient, IEntitiesClientV1):
    def __init__(self, config: Any = None):
        super().__init__('v1.entities')

        if config is not None:
            self.configure(ConfigParams.from_tuples(config))

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        response = self.call_command(
            'get_entities',
            correlation_id,
            {'filter': filter_params, 'paging': paging}
        )
        page = DataPage(
            data=[EntityV1(**item) for item in response['data']],
            total=response['total']
        )
        return page

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        response = self.call_command(
            'get_entity_by_id',
            correlation_id,
            {
                'entity_id': entity_id
            }
        )
        if response:
            return EntityV1(**response)

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        response = self.call_command(
            'get_entity_by_name',
            correlation_id,
            {
                'entity_name': entity_name
            }
        )
        if response:
            return EntityV1(**response)

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        response = self.call_command(
            'create_entity',
            correlation_id,
            {
                'entity': entity
            }
        )
        if response:
            return EntityV1(**response)

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        response = self.call_command(
            'update_entity',
            correlation_id,
            {
                'entity': entity
            }
        )
        if response:
            return EntityV1(**response)

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        response = self.call_command(
            'delete_entity_by_id',
            correlation_id,
            {
                'entity_id': entity_id
            }
        )
        if response:
            return EntityV1(**response)
