# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import FilterParams, PagingParams, DataPage
from pip_services3_rpc.clients import RestClient

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesRestClientV1(RestClient, IEntitiesClientV1):

    def __init__(self, config: Any = None):
        super().__init__()
        self._base_route = "v1/entities"

        if config is not None:
            self.configure(ConfigParams.from_value(config))

    def configure(self, config: ConfigParams):
        super().configure(config)

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        params = {}
        self._add_paging_params(params, paging)
        self._add_filter_params(params, filter_params)

        timing = self._instrument(correlation_id, "v1/entities.get_entities")

        try:
            response = self._call('get',
                                  '/entities',
                                  correlation_id,
                                  params)

            page = DataPage(
                data=[EntityV1(**item) for item in response['data']],
                total=response['total']
            )
            return page
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, "v1/entities.get_entities_by_id")

        try:
            response = self._call('get',
                                  '/entities/' + entity_id,
                                  correlation_id,
                                  None, None)
            if response:
                return EntityV1(**response)

        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        timing = self._instrument(correlation_id, "v1/entities.get_entity_by_name")

        try:
            response = self._call('get',
                                  '/entities/name/' + entity_name,
                                  correlation_id,
                                  None, None)
            if response:
                return EntityV1(**response)

        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, "v1/entities.create_entity")

        try:
            response = self._call('post',
                                  '/entities',
                                  correlation_id,
                                  None,
                                  entity)
            if response:
                return EntityV1(**response)

        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        timing = self._instrument(correlation_id, "v1/entities.update_entity")

        try:
            response = self._call('put',
                                  '/entities',
                                  correlation_id,
                                  None,
                                  entity)
            if response:
                return EntityV1(**response)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        timing = self._instrument(correlation_id, "v1/entities.delete_entity_by_id")

        try:
            response = self._call('delete',
                                  '/entities/' + entity_id,
                                  correlation_id,
                                  None,
                                  None)
            if response:
                return EntityV1(**response)

        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_success()
