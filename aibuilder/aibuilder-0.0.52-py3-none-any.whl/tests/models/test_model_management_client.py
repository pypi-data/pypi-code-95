#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest

from aibuilder.models.model_client_response import ModelClientResponse
from aibuilder.models.model_management_client import ModelManagementClient


def test_model_management_client():
    with pytest.raises(TypeError):
        assert ModelManagementClient()


class DummyModelManagementClient(ModelManagementClient):
    def create(self, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    def delete(self, model_name: str) -> ModelClientResponse:
        pass

    def publish(self, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    def unpublish(self, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    def predict(self, model_name: str, **kwargs: dict) -> ModelClientResponse:
        pass

    def test(self, model_name: str, payload: object) -> ModelClientResponse:
        pass


def test_dummy_model_management_client():
    client = DummyModelManagementClient()

    assert isinstance(client, DummyModelManagementClient)
    assert isinstance(client, ModelManagementClient)
    assert hasattr(client, "create")
    assert hasattr(client, "delete")
    assert hasattr(client, "publish")
    assert hasattr(client, "unpublish")
    assert hasattr(client, "predict")
    assert hasattr(client, "test")
