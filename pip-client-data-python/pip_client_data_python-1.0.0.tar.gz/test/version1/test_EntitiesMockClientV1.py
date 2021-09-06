# -*- coding: utf-8 -*-
from pip_client_data_python.version1.EntitiesMockClientV1 import EntitiesMockClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture


class TestEntitiesMockClientV1:
    client: EntitiesMockClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.client = EntitiesMockClientV1()
        self.fixture = EntitiesClientV1Fixture(self.client)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
