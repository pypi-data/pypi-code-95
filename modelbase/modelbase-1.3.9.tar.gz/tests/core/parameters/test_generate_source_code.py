# type: ignore

import pytest
from modelbase.ode import Model


def test_generate_parameters_source_code():
    model = Model()
    model.add_parameter("k_in", 1, **{"unit": "mM"})
    expected = "m.add_parameters(parameters={'k_in': 1}, meta_info={'k_in': {'unit': 'mM'}})"
    assert expected == model._generate_parameters_source_code(include_meta_info=True)

    expected = "m.add_parameters(parameters={'k_in': 1})"
    assert expected == model._generate_parameters_source_code(include_meta_info=False)
