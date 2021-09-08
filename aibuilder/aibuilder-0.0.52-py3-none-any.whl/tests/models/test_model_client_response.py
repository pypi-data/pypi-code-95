#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest

from aibuilder.models.constants import ModelClientResponseStatus
from aibuilder.models.model_client_response import ModelClientResponse


@pytest.mark.parametrize("status, model_name, model_id, kwargs", [
    (ModelClientResponseStatus.success, "foo", "123", {}),
    (ModelClientResponseStatus.failure, "foobar", "1234", {}),
    (ModelClientResponseStatus.success, "foobar", "1234", {"foo": "bar"}),
])
def test_model_client_response(status, model_name, model_id, kwargs):
    response = ModelClientResponse(status=status, model_name=model_name, model_id=model_id, **kwargs)

    assert isinstance(response, ModelClientResponse)

    assert response.status == status
    assert isinstance(response.status, ModelClientResponseStatus)

    assert response.model_name == model_name
    assert response.model_id == model_id

    if kwargs and isinstance(kwargs, dict):
        sorted(response.status_info.keys()) == sorted(kwargs.keys())
        sorted(response.status_info.values()) == sorted(kwargs.values())
