import pathlib

import pytest

from compredict.connection import Connection
from compredict.exceptions import ClientError, ServerError


def test_set_token(connection):
    token = "hahsduasfbfiuyer"
    connection.set_token(token)

    expected_token = 'Token hahsduasfbfiuyer'

    assert connection.headers['Authorization'] == expected_token


def test_handle_response_with_raising_client_error(connection_with_fail_on_true, response_400):
    with pytest.raises(ClientError):
        connection_with_fail_on_true._Connection__handle_response(response_400)


def test_handle_response_with_raising_server_error(connection_with_fail_on_true, response_500):
    with pytest.raises(ServerError):
        connection_with_fail_on_true._Connection__handle_response(response_500)


def test_handle_response_with_last_error(connection, response_400, response_500):
    response_400 = connection._Connection__handle_response(response_400)
    response_500 = connection._Connection__handle_response(response_500)

    assert response_400 is False
    assert response_500 is False


def test_handle_response_with_graph(connection, response_200_with_url, mocker):
    mocked_wrapper = mocker.patch('tempfile._TemporaryFileWrapper')

    connection._Connection__handle_response(response_200_with_url)

    assert mocked_wrapper.called is True


def test_handle_successful_response(connection, response_200):
    actual_response = connection._Connection__handle_response(response_200)
    expected_response = {
        "error": "False",
        "result": "some result"
    }
    assert actual_response == expected_response


def test_successful_POST(connection, response_200, mocker):
    endpoint = "/some/additional/endpoint"
    data = {"data": "here we have some data"}
    mocker.patch('requests.post', return_value=response_200)
    actual_response = connection.POST(endpoint=endpoint, data=data)

    expected_response = {
        "error": "False",
        "result": "some result"
    }
    assert actual_response == expected_response


def test_successful_POST_with_file(connection, response_200, mocker, data):
    file = pathlib.Path(__file__).parent.resolve().joinpath('example.json')
    mocker.patch('requests.post', return_value=response_200)
    content_type = "json/apllication"
    connection.headers["Content-Type"] = content_type
    actual_result = connection.POST(endpoint="not/as/important/endpoint/here", data=data,
                                    files=file)
    expected = {'error': 'False', 'result': 'some result'}
    assert actual_result == expected
    with pytest.raises(KeyError):
        connection.headers['Content-Type']


def test_unsuccessful_POST(connection, response_400, mocker):
    endpoint = "/some/additional/endpoint"
    data = {"data": "not enough data"}
    mocker.patch('requests.post', return_value=response_400)
    actual_response = connection.POST(endpoint=endpoint, data=data)

    assert actual_response is False


def test_successful_GET(connection, response_200, mocker):
    endpoint = "some/additional/endpoint/get"

    mocker.patch('requests.get', return_value=response_200)

    expected_response = {
        "error": "False",
        "result": "some result"
    }
    actual_response = connection.GET(endpoint=endpoint)

    assert actual_response == expected_response


def test_unsuccessful_GET(connection, response_500, mocker):
    endpoint = "some/additional/endpoint/get"

    mocker.patch('requests.get', return_value=response_500)

    actual_response = connection.GET(endpoint=endpoint)

    assert actual_response is False


def test_create_headers_with_auth():
    connection = Connection(url="not/of/much/importance/here",
                            token="1234token1234")
    actual = connection.headers['Authorization']
    expected = 'Token 1234token1234'
    assert actual == expected
