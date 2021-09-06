# -*- coding: utf-8 -*-
import sys

from pip_service_data_python.logic.EntitiesController import EntitiesController
from pip_service_data_python.persistence.EntitiesMemoryPersistence import EntitiesMemoryPersistence
from pip_service_data_python.services.version1.EntitiesRestServiceV1 import EntitiesRestServiceV1
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_components.log import ConsoleLogger

from pip_client_data_python.version1.EntitiesRestClientV1 import EntitiesRestClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

http_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    "connection.host", "localhost",
    "connection.port", 3000
)


class TestEntitiesRestClientV1:
    service: EntitiesRestServiceV1
    client: EntitiesRestClientV1
    fixture: EntitiesClientV1Fixture

    @classmethod
    def setup_class(cls):
        logger = ConsoleLogger()
        persistence = EntitiesMemoryPersistence()
        controller = EntitiesController()

        cls.service = EntitiesRestServiceV1()
        cls.service.configure(http_config)

        references: References = References.from_tuples(
            Descriptor('pip-services-commons', 'logger', 'console', 'default', '1.0'), logger,
            Descriptor('pip-service-data', 'persistence', 'memory', 'default', '1.0'), persistence,
            Descriptor('pip-service-data', 'controller', 'default', 'default', '1.0'), controller,
            Descriptor('pip-service-data', 'service', 'rest', 'default', '1.0'), cls.service
        )

        controller.set_references(references)
        cls.service.set_references(references)

        cls.client = EntitiesRestClientV1()
        cls.client.set_references(references)
        cls.client.configure(http_config)

        cls.fixture = EntitiesClientV1Fixture(cls.client)

        try:
            cls.service.open(None)
            cls.client.open(None)
        except Exception as ex:
            sys.stderr.write(str(ex))
            raise ex

    @classmethod
    def teardown_class(cls):
        cls.client.close(None)
        cls.service.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
