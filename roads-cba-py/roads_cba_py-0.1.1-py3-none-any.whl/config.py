import json

from schematics import Model
from schematics.types import FloatType, ModelType


class ScenarioGrowthRates(Model):
    motorcycle = FloatType(required=True)
    small_car = FloatType(required=True)
    medium_car = FloatType(required=True)
    delivery = FloatType(required=True)
    four_wheel_drive = FloatType(required=True)
    light_truck = FloatType(required=True)
    medium_truck = FloatType(required=True)
    heavy_truck = FloatType(required=True)
    articulated_truck = FloatType(required=True)
    small_bus = FloatType(required=True)
    medium_bus = FloatType(required=True)
    large_bus = FloatType(required=True)


class GrowthRates(Model):
    very_low = ModelType(ScenarioGrowthRates)
    low = ModelType(ScenarioGrowthRates)
    medium = ModelType(ScenarioGrowthRates)
    high = ModelType(ScenarioGrowthRates)
    very_high = ModelType(ScenarioGrowthRates)


class Config(Model):
    growth_rates = ModelType(GrowthRates, required=True)
    # fleet_characteristics = ModelType(FleetCharacters, required=True)


def load_config(model, file):
    return model(json.load(file))
