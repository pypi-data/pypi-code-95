#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest

from aibuilder.core.model_connection import ModelConnection, LocalFileConnection


def test_model_connection_abstract_class():
    with pytest.raises(TypeError):
        ModelConnection()


def test_local_file_connection(dummy_swagger_file):
    local_file_connection = LocalFileConnection(swagger_file_path=dummy_swagger_file)

    assert isinstance(local_file_connection, ModelConnection)
    assert isinstance(local_file_connection, LocalFileConnection)
    assert hasattr(local_file_connection, "swagger_file_path")
    assert local_file_connection.swagger_file_path == dummy_swagger_file


@pytest.mark.parametrize("local_file_path", ["test_path", "test/path", "/test/path/path1"])
def test_local_file_connection_error(local_file_path, dummy_swagger_file):
    with pytest.raises(ValueError):
        LocalFileConnection(swagger_file_path=local_file_path)

    with pytest.raises(ValueError):
        LocalFileConnection(swagger_file_path=dummy_swagger_file+".test")
