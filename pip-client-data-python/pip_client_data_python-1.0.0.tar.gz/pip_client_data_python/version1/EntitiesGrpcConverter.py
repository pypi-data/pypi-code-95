# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services3_commons.data import PagingParams, DataPage
from pip_services3_commons.errors import ErrorDescriptionFactory, ApplicationException, ErrorDescription, \
    ApplicationExceptionFactory
from pip_services3_grpc.protos.commandable_pb2 import ErrorDescription as ProtoErrorDescription

from pip_service_data_python.data.EntityV1 import EntityV1
from pip_service_data_python.protos.entities_v1_pb2 import Entity as ProtoEntity, EntitiesPage
from pip_service_data_python.protos.entities_v1_pb2 import PagingParams as ProtoPagingParams


class EntitiesGrpcConverterV1:

    @staticmethod
    def from_error(err: Exception) -> Optional[ProtoErrorDescription]:
        if err is None:
            return None

        description = ErrorDescriptionFactory.create(err)
        obj = ProtoErrorDescription()

        obj.type = description.type if description.type is not None else "None"
        obj.category = description.category if description.category is not None else "None"
        obj.code = description.code if description.code is not None else "None"
        obj.correlation_id = description.correlation_id if description.correlation_id is not None else "None"
        obj.status = int(description.status) if description.status is not None else 0
        obj.message = description.message if description.message is not None else "None"
        obj.cause = description.cause if description.cause is not None else "None"
        obj.stack_trace = description.stack_trace if description.stack_trace is not None else "None"

        EntitiesGrpcConverterV1.set_map(obj.details, description.details)

        return obj

    @staticmethod
    def to_error(obj: ProtoErrorDescription) -> Optional[ApplicationException]:
        if obj is None or (obj.category == "" and obj.message == ""):
            return None

        description = ErrorDescription()
        description.type = obj.type
        description.category = obj.category
        description.code = obj.code
        description.correlation_id = obj.correlation_id
        description.status = obj.status
        description.message = obj.message
        description.cause = obj.cause
        description.stack_trace = obj.stack_trace
        description.details = EntitiesGrpcConverterV1.get_map(obj.details)

        return ApplicationExceptionFactory.create(description)

    @staticmethod
    def set_map(map: Any, values: Any) -> Any:
        if values is None:
            return

        if isinstance(values, (list, tuple)):
            for entry in values:
                if isinstance(entry, list):
                    map[0] = entry[1]

        else:
            if isinstance(map, dict):
                for prop_name in values.keys():
                    if values.get(prop_name):
                        map[prop_name] = values[prop_name]
            elif hasattr(values, 'ListFields'):
                for field in values.ListFields():
                    prop_name = field[0].name
                    if getattr(values, prop_name, None):
                        setattr(map, prop_name, getattr(values, prop_name))

    @staticmethod
    def get_map(map: Any) -> Any:
        values = dict()
        EntitiesGrpcConverterV1.set_map(values, map)
        return values

    @staticmethod
    def from_paging_params(paging: PagingParams) -> Optional[ProtoPagingParams]:
        if paging is None:
            return None

        obj = ProtoPagingParams()

        obj.skip = paging.skip or 0
        obj.take = paging.take or 0
        obj.total = paging.total or False

        return obj

    @staticmethod
    def to_paging_params(obj: ProtoPagingParams) -> Optional[PagingParams]:
        if obj is None:
            return

        paging = PagingParams()

        paging.skip = obj.skip
        paging.take = obj.take
        paging.total = obj.total

        return paging

    @staticmethod
    def from_entity(entity: EntityV1) -> Optional[ProtoEntity]:
        if entity is None:
            return

        obj = ProtoEntity()

        obj.id = entity.id or ''
        obj.site_id = entity.site_id or ''
        obj.type = entity.type or ''
        obj.name = entity.name or ''
        obj.content = entity.content or ''

        return obj

    @staticmethod
    def to_entity(obj: ProtoEntity) -> Optional[EntityV1]:
        if obj is None:
            return

        entity = EntityV1(id=obj.id,
                          site_id=obj.site_id,
                          type=obj.type,
                          name=obj.name,
                          content=obj.content)

        return entity

    @staticmethod
    def from_entities_page(page: DataPage) -> Optional[EntitiesPage]:
        if page is None:
            return

        obj = EntitiesPage()

        obj.total = page.total

        for item in page.data:
            obj.data.append(EntitiesGrpcConverterV1.from_entity(item))

        return obj

    @staticmethod
    def to_entities_page(obj: EntitiesPage) -> Optional[DataPage]:
        if obj is None:
            return

        data = []

        for item in obj.data:
            data.append(EntitiesGrpcConverterV1.to_entity(item))

        return DataPage(total=obj.total, data=data)
