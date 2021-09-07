from pollination.honeybee_energy.translate import ModelToOsm, ModelOccSchedules
from queenbee.plugin.function import Function


def test_model_to_osm():
    function = ModelToOsm().queenbee
    assert function.name == 'model-to-osm'
    assert isinstance(function, Function)


def test_model_occ_schedules():
    function = ModelOccSchedules().queenbee
    assert function.name == 'model-occ-schedules'
    assert isinstance(function, Function)
