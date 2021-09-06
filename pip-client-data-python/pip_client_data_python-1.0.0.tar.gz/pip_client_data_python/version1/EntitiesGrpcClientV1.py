# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_commons.data import FilterParams, DataPage, PagingParams
from pip_services3_grpc.clients.GrpcClient import GrpcClient

from pip_client_data_python.protos import entities_v1_pb2 as messages, entities_v1_pb2_grpc
from pip_client_data_python.version1.EntitiesGrpcConverter import EntitiesGrpcConverterV1
from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesGrpcClientV1(GrpcClient, IEntitiesClientV1):

    def __init__(self):
        super().__init__(entities_v1_pb2_grpc.EntitiesStub, 'entities_v1')

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        request = messages.EntitiesPageRequest(paging=EntitiesGrpcConverterV1.from_paging_params(paging))
        EntitiesGrpcConverterV1.set_map(request.filter, filter_params)

        timing = self._instrument(correlation_id, 'v1.entities.get_entities')

        try:
            response = self._call('get_entities', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.page else EntitiesGrpcConverterV1.to_entities_page(response.page)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        request = messages.EntityIdRequest()

        timing = self._instrument(correlation_id, 'v1.entities.get_entities_by_id')

        try:
            response = self._call('get_entity_by_id', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.entity.id else EntitiesGrpcConverterV1.to_entity(response.entity)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> Optional[EntityV1]:
        request = messages.EntityNameRequest(name=entity_name)

        timing = self._instrument(correlation_id, 'v1.entities.get_entity_by_name')

        try:
            response = self._call('get_entity_by_name', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.entity.id else EntitiesGrpcConverterV1.to_entity(response.entity)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        grpc_entity = EntitiesGrpcConverterV1.from_entity(entity)
        request = messages.EntityRequest(entity=grpc_entity)

        timing = self._instrument(correlation_id, 'v1.entities.create_entity')

        try:
            response = self._call('create_entity', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.entity.id else EntitiesGrpcConverterV1.to_entity(response.entity)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        grpc_entity = EntitiesGrpcConverterV1.from_entity(entity)
        request = messages.EntityRequest(entity=grpc_entity)

        timing = self._instrument(correlation_id, 'v1.entities.update_entity')

        try:
            response = self._call('update_entity', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.entity.id else EntitiesGrpcConverterV1.to_entity(response.entity)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        request = messages.EntityIdRequest(entity_id=entity_id)

        timing = self._instrument(correlation_id, 'v1.entities.delete_entity_by_id')

        try:
            response = self._call('delete_entity_by_id', correlation_id, request)

            if response.error.category:
                err = EntitiesGrpcConverterV1.to_error(response.error)
                raise err

            result = None if not response.entity.id else EntitiesGrpcConverterV1.to_entity(response.entity)

            return result
        except Exception as err:
            timing.end_timing(err)
        finally:
            timing.end_success()
