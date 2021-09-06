# -*- coding: utf-8 -*-
from pip_services3_commons.data import IdGenerator
from pip_services3_commons.random import RandomString, RandomInteger

from pip_client_data_python.version1.EntityTypeV1 import EntityTypeV1
from pip_client_data_python.version1.EntityV1 import EntityV1


class RandomEntityV1:

    @staticmethod
    def next_entity(site_count: int = 100) -> EntityV1:
        return EntityV1(id=IdGenerator.next_long(),
                        site_id=RandomEntityV1.next_site_id(site_count),
                        type=RandomEntityV1.next_entity_type(),
                        name=RandomString.next_string(10, 25),
                        content=RandomString.next_string(0, 50))

    @staticmethod
    def next_site_id(site_count: int = 100) -> str:
        return str(RandomInteger.next_integer(1, site_count))

    @staticmethod
    def next_entity_type() -> str:
        choice = RandomInteger.next_integer(0, 3)
        if choice == 0:
            return EntityTypeV1.Type2
        if choice == 1:
            return EntityTypeV1.Type1
        if choice == 2:
            return EntityTypeV1.Type3
        if choice == 3:
            return EntityTypeV1.Type2
        else:
            return EntityTypeV1.Unknown
