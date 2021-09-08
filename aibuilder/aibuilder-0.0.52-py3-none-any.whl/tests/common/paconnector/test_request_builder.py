#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

from collections import OrderedDict
from unittest.mock import patch

import pytest

from aibuilder.common.paconnector.constants import RequestBuilderConstants
from aibuilder.common.paconnector.exceptions import DuplicateModelException, RequestFormatException
from aibuilder.common.paconnector.request_builder import _RequestBuilder


@pytest.mark.parametrize("url, scheme, netloc, base_path", [
    ("https://foobar.com/test/path", "https", "foobar.com", "/"),
    ("https://us.foobar.com/test/path", "https", "us.foobar.com", "/"),
    ("http://foobar.com/test/path", "http", "foobar.com", "org/path/"),
    ("https://foobar.org.us", "https", "foobar.org.us", "temp/"),
    ("https://foobar.org.us", "https", "foobar.org.us", "test/path/ok/"),
])
def test_request_builder_init(url, scheme, netloc, base_path):
    request_builder = _RequestBuilder(url=url, base_path=base_path)

    isinstance(request_builder, _RequestBuilder)
    assert request_builder._scheme == scheme
    assert request_builder._netloc == netloc
    assert request_builder._base_path == base_path
    assert request_builder._token == ""
    assert request_builder._api_version is None


@pytest.mark.parametrize("url, scheme, netloc, base_path, path, query, expected_endpoint", [
    ("https://foobar.com/test/path", "https", "foobar.com", "", "", {"q": "val"}, "https://foobar.com/?q=val"),
    ("https://us.foobar.com/test/path", "https", "us.foobar.com", "", "", {"a": "b"}, "https://us.foobar.com/?a=b"),
    ("http://foobar.com/test/path", "http", "foobar.com", "org/path", "test", None, "http://foobar.com/org/path/test"),
    ("https://foobar.org.us", "https", "foobar.org.us", "temp", "", None, "https://foobar.org.us/temp/"),
    ("https://foobar.org.us", "https", "foobar.org.us", "test/path/ok", "", OrderedDict({"v1": "a", "v2": "b"}),
     "https://foobar.org.us/test/path/ok/?v1=a&v2=b"),
])
def test_construct_url(url, scheme, netloc, base_path, path, query, expected_endpoint):
    request_builder = _RequestBuilder(url=url, base_path=base_path)

    endpoint = request_builder.construct_url(path=path, query=query)

    assert expected_endpoint == endpoint


@pytest.mark.parametrize("method, endpoint, headers, payload", [
    (RequestBuilderConstants.GET, "https://foobar.com", {"test": "header"}, ""),
    (RequestBuilderConstants.POST, "https://foobar.com", None, "{'test':'value'}"),
    (RequestBuilderConstants.GET, "https://foobar.com", None, ""),
    (RequestBuilderConstants.GET, "https://foobar.com", {"test": "header"}, "{'test':'value'}"),
])
@pytest.mark.parametrize("status_code, expected_exception", [
    (200, None),
    (412, DuplicateModelException),
    (400, RequestFormatException),
])
def test_request(method, endpoint, headers, payload, status_code, expected_exception, request_builder):
    def validate_response():
        assert response.status_code == status_code

        assert mock_request.call_count == 1
        assert mock_request.call_args[0][0] == method.value
        assert mock_request.call_args[0][1] == endpoint
        if headers:
            assert list(mock_request.call_args[1]["headers"].keys()) == list(headers.keys())
            assert list(mock_request.call_args[1]["headers"].values()) == list(headers.values())
        assert mock_request.call_args[1]["json"] == payload

    with patch('requests.request') as mock_request:
        mock_request.return_value.status_code = status_code

        if expected_exception is None:
            response = request_builder.request(method=method, endpoint=endpoint, headers=headers, payload=payload)
            validate_response()
        else:
            mock_request.side_effect = expected_exception.__call__(message="")
            with pytest.raises(expected_exception):
                response = request_builder.request(method=method, endpoint=endpoint, headers=headers, payload=payload)

                validate_response()
