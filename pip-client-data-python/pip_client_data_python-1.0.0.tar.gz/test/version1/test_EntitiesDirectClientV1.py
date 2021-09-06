# -*- coding: utf-8 -*-
from pip_service_data_python.logic.EntitiesController import EntitiesController
from pip_service_data_python.persistence.EntitiesMemoryPersistence import EntitiesMemoryPersistence
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from pip_client_data_python.version1.EntitiesDirectClientV1 import EntitiesDirectClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture


class TestEntitiesDirectClientV1:
    persistence: EntitiesMemoryPersistence
    controller: EntitiesController
    client: EntitiesDirectClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.persistence = EntitiesMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.controller = EntitiesController()
        self.controller.configure(ConfigParams())

        self.client = EntitiesDirectClientV1()

        references = References.from_tuples(
            Descriptor('pip-service-data', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('pip-service-data', 'controller', 'default', 'default', '1.0'), self.controller,
            Descriptor('pip-service-data', 'client', 'direct', 'default', '1.0'), self.client
        )

        self.controller.set_references(references)
        self.client.set_references(references)

        self.fixture = EntitiesClientV1Fixture(self.client)

        self.persistence.open(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
