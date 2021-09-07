from pollination.lbt_honeybee.edit import ModelModifiersFromConstructions
from queenbee.plugin.function import Function


def test_model_modifiers_from_constructions():
    function = ModelModifiersFromConstructions().queenbee
    assert function.name == 'model-modifiers-from-constructions'
    assert isinstance(function, Function)
