# -*- coding: utf-8 -*-
from pip_service_data_python.logic.EntitiesController import EntitiesController
from pip_service_data_python.persistence.EntitiesMemoryPersistence import EntitiesMemoryPersistence
from pip_service_data_python.services.version1.EntitiesCommandableGrpcServiceV1 import EntitiesCommandableGrpcServiceV1
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References

from pip_client_data_python.version1.EntitiesCommandableGrpcClientV1 import EntitiesCommandableGrpcClientV1
from test.version1.EntitiesClientV1Fixture import EntitiesClientV1Fixture

grpc_config = ConfigParams.from_tuples(
    'connection.protocol', 'http',
    'connection.host', 'localhost',
    'connection.port', 3000
)


class TestEntitiesCommandableGrpcClientV1:
    persistence: EntitiesMemoryPersistence
    controller: EntitiesController
    service: EntitiesCommandableGrpcServiceV1
    client: EntitiesCommandableGrpcClientV1
    fixture: EntitiesClientV1Fixture

    def setup_method(self):
        self.persistence = EntitiesMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.controller = EntitiesController()
        self.controller.configure(ConfigParams())

        self.service = EntitiesCommandableGrpcServiceV1()
        self.service.configure(grpc_config)

        self.client = EntitiesCommandableGrpcClientV1()
        self.client.configure(grpc_config)

        references = References.from_tuples(
            Descriptor('pip-service-data', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('pip-service-data', 'controller', 'default', 'default', '1.0'), self.controller,
            Descriptor('pip-service-data', 'service', 'grpc', 'default', '1.0'), self.service,
            Descriptor('pip-service-data', 'client', 'grpc', 'default', '1.0'), self.client
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
