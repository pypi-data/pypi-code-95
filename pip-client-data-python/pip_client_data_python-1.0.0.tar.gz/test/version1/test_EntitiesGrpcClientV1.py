# -*- coding: utf-8 -*-

from pip_service_data_python.logic.EntitiesController import EntitiesController
from pip_service_data_python.persistence.EntitiesMemoryPersistence import EntitiesMemoryPersistence
from pip_service_data_python.services.version1.EntitiesGrpcServiceV1 import EntitiesGrpcServiceV1
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor

from pip_client_data_python.version1.EntitiesGrpcClientV1 import EntitiesGrpcClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

grpc_config = ConfigParams.from_tuples(
    'connection.protocol', 'http',
    'connection.host', 'localhost',
    'connection.port', 3000
)


class TestEntitiesGrpcClientV1:
    persistence: EntitiesMemoryPersistence
    controller: EntitiesController
    service: EntitiesGrpcServiceV1
    client: EntitiesGrpcClientV1
    fixture: EntitiesClientV1Fixture

    @classmethod
    def setup_class(cls):
        cls.persistence = EntitiesMemoryPersistence()
        cls.persistence.configure(ConfigParams())

        cls.controller = EntitiesController()
        cls.controller.configure(ConfigParams())

        cls.service = EntitiesGrpcServiceV1()
        cls.service.configure(grpc_config)

        cls.client = EntitiesGrpcClientV1()
        cls.client.configure(grpc_config)

        references: References = References.from_tuples(
            Descriptor('pip-service-data', 'persistence', 'memory', 'default', '1.0'), cls.persistence,
            Descriptor('pip-service-data', 'controller', 'default', 'default', '1.0'), cls.controller,
            Descriptor('pip-service-data', 'service', 'grpc', 'default', '1.0'), cls.service,
            Descriptor('pip-service-data', 'client', 'grpc', 'default', '1.0'), cls.client
        )

        cls.controller.set_references(references)
        cls.service.set_references(references)
        cls.client.set_references(references)

        cls.fixture = EntitiesClientV1Fixture(cls.client)

        cls.persistence.open(None)
        cls.service.open(None)
        cls.client.open(None)

    @classmethod
    def teardown_class(cls):
        cls.client.close(None)
        cls.service.close(None)
        cls.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
