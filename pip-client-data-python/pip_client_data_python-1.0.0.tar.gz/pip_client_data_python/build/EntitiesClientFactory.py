# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from pip_client_data_python.version1 import EntitiesNullClientV1
from pip_client_data_python.version1.EntitiesCommandableGrpcClientV1 import EntitiesCommandableGrpcClientV1
from pip_client_data_python.version1.EntitiesCommandableHttpClientV1 import EntitiesCommandableHttpClientV1
from pip_client_data_python.version1.EntitiesCommandableLambdaClientV1 import EntitiesCommandableLambdaClientV1
from pip_client_data_python.version1.EntitiesDirectClientV1 import EntitiesDirectClientV1
from pip_client_data_python.version1.EntitiesMockClientV1 import EntitiesMockClientV1


# from pip_client_data_python.version1.EntitiesGrpcClientV1 import EntitiesGrpcClientV1
# from pip_client_data_python.version1.EntitiesLambdaClientV1 import EntitiesLambdaClientV1
# from pip_client_data_python.version1.EntitiesRestClientV1 import EntitiesRestClientV1


class EntitiesClientFactory(Factory):
    __NullClientDescriptor = Descriptor('pip-service-data', 'client', 'null', '*', '1.0')
    __DirectClientDescriptor = Descriptor('pip-service-data', 'client', 'direct', '*', '1.0')
    __CommandableHttpClientDescriptor = Descriptor('pip-service-data', 'client', 'commandable-http', '*', '1.0')
    __CommandableGrpcClientV1Descriptor = Descriptor('pip-service-data', 'client', 'commandable-grpc', '*', '1.0')
    __CommandableLambdaClientV1Descriptor = Descriptor('pip-service-data', 'client', 'commandable-lambda', '*', '1.0')
    __LambdaClientV1Descriptor = Descriptor('pip-service-data', 'client', 'lambda', 'default', '1.0')
    __GrpcClientV1Descriptor = Descriptor('pip-service-data', 'client', 'grpc', '*', '1.0')
    __RestClientV1Descriptor = Descriptor('pip-service-data', 'client', 'rest', '*', '1.0')
    __EntitiesMockClientV1Descriptor = Descriptor('pip-service-data', 'client', 'mock', '*', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(EntitiesClientFactory.__NullClientDescriptor, EntitiesNullClientV1)
        self.register_as_type(EntitiesClientFactory.__EntitiesMockClientV1Descriptor, EntitiesMockClientV1)
        self.register_as_type(EntitiesClientFactory.__DirectClientDescriptor, EntitiesDirectClientV1)
        self.register_as_type(EntitiesClientFactory.__CommandableHttpClientDescriptor, EntitiesCommandableHttpClientV1)
        self.register_as_type(EntitiesClientFactory.__CommandableGrpcClientV1Descriptor,
                              EntitiesCommandableGrpcClientV1)
        self.register_as_type(EntitiesClientFactory.__CommandableLambdaClientV1Descriptor,
                              EntitiesCommandableLambdaClientV1)

        # self.register_as_type(EntitiesClientFactory.__RestClientV1Descriptor, EntitiesRestClientV1)
        # self.register_as_type(EntitiesClientFactory.__GrpcClientV1Descriptor, EntitiesGrpcClientV1)
        # self.register_as_type(EntitiesClientFactory.__LambdaClientV1Descriptor, EntitiesLambdaClientV1)
