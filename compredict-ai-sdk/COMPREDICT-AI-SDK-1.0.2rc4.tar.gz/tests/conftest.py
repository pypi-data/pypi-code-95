import json

import pytest
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from requests import Response

from compredict.client import api
from compredict.connection import Connection
from compredict.resources import Task


@pytest.fixture(scope='session')
def rsa_key():
    generated_key = RSA.generate(1024)
    rsa_key = PKCS1_OAEP.new(generated_key)
    return rsa_key


@pytest.fixture(scope='session')
def api_client(rsa_key):
    api_client = api.get_instance()
    api_client.rsa_key = rsa_key
    return api_client


@pytest.fixture(scope='session')
def connection():
    connection = Connection(url="https://core.compredict.ai/api/")
    return connection


@pytest.fixture(scope="session")
def unsucessful_content():
    unsucessful_content = {
        'error': "True",
        'error_msg': 'Bad request'

    }
    return unsucessful_content


@pytest.fixture(scope="session")
def successful_content():
    successful_content = {
        "error": "False",
        "result": "some result"
    }
    return successful_content


@pytest.fixture(scope="session")
def response_400(unsucessful_content):
    response = Response()
    response.status_code = 400
    response._content = json.dumps(unsucessful_content).encode('utf-8')
    return response


@pytest.fixture(scope="session")
def response_500(unsucessful_content):
    response = Response()
    response.status_code = 500
    response._content = json.dumps(unsucessful_content).encode('utf-8')
    return response


@pytest.fixture(scope="session")
def response_200(successful_content):
    response_200 = Response()
    response_200.status_code = 200
    response_200._content = json.dumps(successful_content).encode('utf-8')
    response_200.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    response_200.headers['Content-Type'] = 'application/json'
    return response_200


@pytest.fixture(scope="session")
def response_200_with_url(successful_content):
    response_200_with_url = Response()
    response_200_with_url.status_code = 200
    response_200_with_url._content = json.dumps(successful_content).encode('utf-8')
    response_200_with_url.url = 'https://core.compredict.ai/api/v1/algorithms/56/graph'
    response_200_with_url.headers['Content-Type'] = 'image/png'
    return response_200_with_url


@pytest.fixture(scope="session")
def response_200_with_versions(versions):
    response_200_with_versions = Response()
    response_200_with_versions.status_code = 200
    response_200_with_versions._content = json.dumps(versions).encode('utf-8')
    response_200_with_versions.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    response_200_with_versions.headers['Content-Type'] = 'application/json'
    return response_200_with_versions


@pytest.fixture(scope="session")
def response_200_with_version(versions):
    response_200_with_version = Response()
    response_200_with_version.status_code = 200
    response_200_with_version._content = json.dumps(versions[0]).encode('utf-8')
    response_200_with_version.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    response_200_with_version.headers['Content-Type'] = 'application/json'
    return response_200_with_version


@pytest.fixture(scope="session")
def response_200_with_result(result):
    response_200_with_result = Response()
    response_200_with_result.status_code = 200
    response_200_with_result._content = json.dumps(result).encode('utf-8')
    response_200_with_result.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    response_200_with_result.headers['Content-Type'] = 'application/json'
    return response_200_with_result


@pytest.fixture(scope="session")
def response_200_with_algorithm(algorithm):
    response_200_with_algorithm = Response()
    response_200_with_algorithm.status_code = 200
    response_200_with_algorithm._content = json.dumps(algorithm).encode('utf-8')
    response_200_with_algorithm.headers['Content-Type'] = 'application/json'
    response_200_with_algorithm.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    return response_200_with_algorithm


@pytest.fixture(scope="session")
def response_200_with_algorithms(algorithm):
    algorithms = [algorithm, algorithm, algorithm]
    response_200_with_algorithms = Response()
    response_200_with_algorithms.status_code = 200
    response_200_with_algorithms._content = json.dumps(algorithms).encode('utf-8')
    response_200_with_algorithms.headers['Content-Type'] = 'application/json'
    response_200_with_algorithms.url = 'https://core.compredict.ai/api/v1/algorithms/56'
    return response_200_with_algorithms


@pytest.fixture(scope='session')
def connection_with_fail_on_true():
    connection_with_fail_on_true = Connection(url="https://core.compredict.ai/api/")
    connection_with_fail_on_true.fail_on_error = True
    return connection_with_fail_on_true


@pytest.fixture(scope='session')
def task():
    task = Task()
    return task


@pytest.fixture(scope='session')
def object():
    object = {
        "status": "In Progress"
    }
    return object


@pytest.fixture(scope='session')
def data():
    data = {"1": [346.5, 6456.6, 56.7], "2": [343.4, 34.6, 45.7]}
    return data


@pytest.fixture(scope='session')
def versions():
    versions = [{
        'version': '1.3.0',
        'change_description': 'New features added',
        'results': 'All the requests will be send to queue system',
        'features_format': [],
        'output_format': []
    },
        {
            'version': '1.4.0',
            'change_description': 'Even more features added',
            'results': 'All the requests will be send to queue system',
            'features_format': [],
            'output_format': []
        }]
    return versions


@pytest.fixture(scope='session')
def result():
    result = {
        'reference': '12jffd',
        'status': "Finished",
        'is_encrypted': False,
        'results': []
    }
    return result


@pytest.fixture(scope='session')
def algorithm():
    algorithm = {
        'id': 'mass_estimation',
        'name': 'Mass Estimation',
        'description': 'Some description',
        'versions': [{'mass_estimation': '1.0.0'}, {'mass_estimation': '2.0.0'}],
        'evaluations': []
    }
    return algorithm
