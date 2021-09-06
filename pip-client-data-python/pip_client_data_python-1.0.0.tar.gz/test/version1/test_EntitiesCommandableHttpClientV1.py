# -*- coding: utf-8 -*-
from pip_service_data_python.logic.EntitiesController import EntitiesController
from pip_service_data_python.persistence.EntitiesMemoryPersistence import EntitiesMemoryPersistence
from pip_service_data_python.services.version1.EntitiesCommandableHttpServiceV1 import EntitiesCommandableHttpServiceV1
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from pip_client_data_python.version1.EntitiesCommandableHttpClientV1 import EntitiesCommandableHttpClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

http_config = ConfigParams.from_tuples(
    'connection.protocol', 'http',
    'connection.host', 'localhost',
    'connection.port', 3000
)


class TestEntitiesCommandableHttpClientV1:
    persistence: EntitiesMemoryPersistence
    controller: EntitiesController
    service: EntitiesCommandableHttpServiceV1
    client: EntitiesCommandableHttpClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.persistence = EntitiesMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.controller = EntitiesController()
        self.controller.configure(ConfigParams())

        self.service = EntitiesCommandableHttpServiceV1()
        self.service.configure(http_config)

        self.client = EntitiesCommandableHttpClientV1()
        self.client.configure(http_config)

        references = References.from_tuples(
            Descriptor('pip-service-data', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('pip-service-data', 'controller', 'default', 'default', '1.0'), self.controller,
            Descriptor('pip-service-data', 'service', 'http', 'default', '1.0'), self.service,
            Descriptor('pip-service-data', 'client', 'http', 'default', '1.0'), self.client
        )

        self.controller.set_references(references)
        self.service.set_references(references)
        self.client.set_references(references)

        self.fixture = EntitiesClientV1Fixture(self.client)

        self.persistence.open(None)
        self.service.open(None)
        self.client.open(None)

    def teardown_method(self):
        self.persistence.close(None)
        self.service.close(None)
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
