#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest
from aibuilder.common.utils import Credentials


@pytest.mark.parametrize("username, password", [
    ("test", "foobar"),
    ("foo", "bar")
])
def test_credentials_namedtuple_creation(username, password):
    credentials = Credentials(username=username, password=password)

    assert isinstance(credentials, Credentials)
    assert hasattr(credentials, "username")
    assert hasattr(credentials, "password")
    assert credentials.username == username
    assert credentials.password == password
