#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest

from aibuilder.common.paconnector.request_builder import _RequestBuilder


@pytest.fixture
def request_builder():
    return _RequestBuilder(url="http://foobar.com", base_path="base")
