# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_commons.data import FilterParams, PagingParams, DataPage

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class TestEntitiesNullClientV1(IEntitiesClientV1):
    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        return None

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> Optional[EntityV1]:
        return None

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        return None

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        return None

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        return None

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        return DataPage([], 0)
