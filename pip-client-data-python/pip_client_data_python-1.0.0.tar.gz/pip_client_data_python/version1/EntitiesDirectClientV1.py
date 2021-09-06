# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_commons.data import DataPage, FilterParams, PagingParams
from pip_services3_commons.refer import Descriptor
from pip_services3_rpc.clients import DirectClient

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesDirectClientV1(DirectClient, IEntitiesClientV1):
    def __init__(self):
        super().__init__()

        self._dependency_resolver.put('controller', Descriptor('pip-service-data', 'controller', '*', '*', '1.0'))

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        timing = self._instrument(correlation_id, 'entities.get_entities')
        try:
            return self._controller.get_entities(correlation_id, filter_params, paging)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'entities.get_entity_by_id')
        try:
            return self._controller.get_entities_by_id(correlation_id, entity_id)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'entities.get_entity_by_name')
        try:
            return self._controller.get_entity_by_name(correlation_id, entity_name)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, 'entities.create_entity')
        try:
            return self._controller.create_entity(correlation_id, entity)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, 'entities.update_entity')
        try:
            return self._controller.update_entity(correlation_id, entity)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'entities.delete_entity_by_id')
        try:
            return self._controller.delete_entity_by_id(correlation_id, entity_id)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()
