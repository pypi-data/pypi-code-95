# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_commons.data import DataPage, PagingParams, FilterParams
from pip_services3_grpc.clients.CommandableGrpcClient import CommandableGrpcClient

from pip_client_data_python.version1.EntitiesGrpcConverter import EntitiesGrpcConverterV1
from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesCommandableGrpcClientV1(CommandableGrpcClient, IEntitiesClientV1):

    def __init__(self, config: Any = None):
        super().__init__('v1.entities')

        if config is not None:
            self.configure(config)

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        resultPage = self.call_command(
            'get_entities',
            correlation_id,
            {'filter': filter_params, 'paging': paging}
        )

        page = DataPage(data=[EntitiesGrpcConverterV1.to_entity(item) for item in resultPage.data],
                        total=resultPage.total)
        return page

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        result = self.call_command(
            'get_entity_by_id',
            correlation_id,
            {
                'entity_id': entity_id
            }
        )
        return EntitiesGrpcConverterV1.to_entity(result)

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        result = self.call_command(
            'get_entity_by_name',
            correlation_id,
            {
                'entity_name': entity_name
            }
        )

        return EntitiesGrpcConverterV1.to_entity(result)

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        result = self.call_command(
            'create_entity',
            correlation_id,
            {
                'entity': entity
            }
        )
        return EntitiesGrpcConverterV1.to_entity(result)

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        result = self.call_command(
            'update_entity',
            correlation_id,
            {
                'entity': entity
            }
        )
        return EntitiesGrpcConverterV1.to_entity(result)

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        result = self.call_command(
            'delete_entity_by_id',
            correlation_id,
            {
                'entity_id': entity_id
            }
        )

        return EntitiesGrpcConverterV1.to_entity(result)
