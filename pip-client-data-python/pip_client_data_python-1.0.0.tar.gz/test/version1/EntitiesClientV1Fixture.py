# -*- coding: utf-8 -*-
from pip_services3_commons.data import FilterParams, PagingParams

from pip_client_data_python.version1.EntityTypeV1 import EntityTypeV1
from pip_client_data_python.version1.EntityV1 import EntityV1
from pip_client_data_python.version1.IEntitiesClientV1 import IEntitiesClientV1

ENTITY1 = EntityV1(
    id='1',
    name='00001',
    type=EntityTypeV1.Type1,
    site_id='1',
    content='ABC'
)

ENTITY2 = EntityV1(
    id='2',
    name='00002',
    type=EntityTypeV1.Type2,
    site_id='1',
    content='XYZ'
)


class EntitiesClientV1Fixture:
    __client: IEntitiesClientV1

    def __init__(self, client: IEntitiesClientV1):
        assert client is not None
        self.__client = client

    def test_crud_operations(self):
        # Create the first entity
        entity = self.__client.create_entity(None, ENTITY1)
        assert ENTITY1.name == entity.name
        assert ENTITY1.site_id == entity.site_id
        assert ENTITY1.type == entity.type
        assert ENTITY1.name == entity.name
        assert entity.content is not None

        entity = self.__client.create_entity(None, ENTITY2)
        assert ENTITY2.name == entity.name
        assert ENTITY2.site_id == entity.site_id
        assert ENTITY2.type == entity.type
        assert ENTITY2.name == entity.name
        assert entity.content is not None

        # Get all entities
        page = self.__client.get_entities(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        entity1 = page.data[0]

        # Update the entity
        entity1.name = 'ABC'

        entity = self.__client.update_entity(None, entity1)
        assert entity is not None
        assert entity.id == entity1.id
        assert 'ABC' == entity.name

        # Get entity by name
        entity = self.__client.get_entity_by_name(None, entity1.name)
        assert entity is not None
        assert entity.name == entity1.name

        # Delete the entity
        entity = self.__client.delete_entity_by_id(None, entity1.id)
        assert entity1 is not None
        assert entity.id == entity1.id

        # Try to get deleted entity
        entity = self.__client.get_entities_by_id(None, entity1.id)
        assert entity is None
