# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import List, Callable, Optional

from pip_services3_commons.data import FilterParams, DataPage, PagingParams

from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1


class EntitiesMockClientV1(IEntitiesClientV1):

    def __init__(self, items: List[EntityV1] = None):
        self.__items: List[EntityV1] = deepcopy(items) or []

        self.__max_page_size = 100

    def __compose_filter(self, filter_params: FilterParams) -> Callable[[EntityV1], bool]:
        filter_params = filter_params or FilterParams()

        id = filter_params.get_as_nullable_string('id')
        site_id = filter_params.get_as_nullable_string('site_id')
        name = filter_params.get_as_nullable_string('name')

        tempNames = filter_params.get_as_nullable_string('names')
        names = None if not tempNames else tempNames.split(',')

        def inner(item: EntityV1) -> bool:
            if id is not None and item.id != id:
                return False
            if site_id is not None and item.site_id != site_id:
                return False
            if name is not None and item.name != name:
                return False
            if names is not None and item.name in names:
                return False

            return True

        return inner

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        filters_entities = self.__compose_filter(filter_params)
        entities = list(filter(filters_entities, self.__items))

        # Extract a page
        paging = paging or PagingParams()
        skip = paging.skip
        take = paging.take
        total = paging.total

        if paging.total:
            total = len(entities)
        if skip and skip > 0:
            entities = entities[skip:]

        entities = entities[0:take]
        return DataPage(entities, total)

    def get_entities_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        entities = list(filter(lambda x: x.id == entity_id, self.__items))

        entity = None if len(entities) < 1 else entities[0]
        return entity

    def get_entity_by_name(self, correlation_id: Optional[str], entity_name: str) -> EntityV1:
        entities = list(filter(lambda x: x.name == entity_name, self.__items))

        entity = None if len(entities) < 1 else entities[0]
        return entity

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        if entity is None:
            return None

        entity = deepcopy(entity)

        self.__items.append(entity)
        return entity

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        index = -1

        for i in range(len(self.__items)):
            if self.__items[i].id == entity.id:
                index = i
                break

        if index < 0:
            return None

        entity = deepcopy(entity)

        self.__items[index] = entity
        return entity

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        index = -1

        for i in range(len(self.__items)):
            if self.__items[i].id == entity_id:
                index = i
                break

        if index < 0:
            return None

        entity = self.__items[index]
        del self.__items[index]
        return entity
