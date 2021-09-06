# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_aws.clients.LambdaClient import LambdaClient
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import DataPage, PagingParams, FilterParams

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesLambdaClientV1(LambdaClient, IEntitiesClientV1):

    def __init__(self, config: Any = None):
        super().__init__()

        if config is not None:
            self.configure(ConfigParams.from_value(config))

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        timing = self._instrument(correlation_id, 'v1.entities.get_entities')

        try:
            response = self._call('v1.entities.get_entities',
                                  correlation_id,
                                  {'filter': filter_params, 'paging': paging}, )
            page = DataPage(
                data=[EntityV1(**item) for item in response['data']],
                total=response['total']
            )
            return page
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'v1.entities.get_entity_by_id')

        try:
            response = self._call('v1.entities.get_entity_by_id',
                                  correlation_id,
                                  {
                                      'entity_id': entity_id
                                  })
            if response:
                return EntityV1(**response)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'v1.entities.get_entity_by_name')

        try:
            response = self._call('v1.entities.get_entity_by_name',
                                  correlation_id,
                                  {
                                      'entity_name': entity_name
                                  })
            if response:
                return EntityV1(**response)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, 'v1.entities.create_entity')

        try:
            response = self._call('v1.entities.create_entity',
                                  correlation_id,
                                  {
                                      'entity': entity
                                  })
            if response:
                return EntityV1(**response)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, 'v1.entities.update_entity')

        try:
            response = self._call('v1.entities.update_entity',
                                  correlation_id,
                                  {
                                      'entity': entity
                                  })
            if response:
                return EntityV1(**response)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, 'v1.entities.delete_entity_by_id')

        try:
            response = self._call('v1.entities.delete_entity_by_id',
                                  correlation_id,
                                  {
                                      'entity_id': entity_id
                                  })
            if response:
                return EntityV1(**response)
        except Exception as ex:
            timing.end_failure(ex)
        finally:
            timing.end_success()
