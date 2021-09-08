#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import pytest

from aibuilder.models.helpers.data_model_operator import DataModelOperator


def test_data_model_operator_init():
    with pytest.raises(TypeError):
        DataModelOperator(url="http://foobar.com", token="token")
