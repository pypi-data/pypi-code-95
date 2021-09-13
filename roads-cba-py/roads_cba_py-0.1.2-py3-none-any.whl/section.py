import json
from os import stat
from typing import List, Optional
from schematics.exceptions import ConversionError

from schematics.models import Model
from schematics.types import IntType, StringType, FloatType


class InvalidSection(object):
    def __init__(self, errors, original_data):
        self.errors = InvalidSection.clean_errors(errors)
        self.original_data = original_data

    def invalid_reason(self):
        return self.errors

    @staticmethod
    def clean_errors(errors):
        return [InvalidSection.clean_error(k, v) for k, v in errors.items()]

    @staticmethod
    def clean_error(k, v):
        # print(type(v), v)
        # print(type(k), k)
        # print(isinstance(v, ConversionError))
        if isinstance(v, ConversionError):
            return f"Invalid characters in '{k}', expected float"
        return f"Generic error: {k}"


def parse_section(json):
    try:
        return Section(json)
    except Exception as err:
        return InvalidSection(err.errors, json)


class Section(Model):
    orma_way_id = StringType(max_length=20, min_length=1, required=True)
    vpromm_id = StringType(max_length=20, min_length=1)
    # section_id = StringType(max_length=30, required=True)
    road_number = StringType(max_length=10)
    road_name = StringType(max_length=255, min_length=1)
    road_start = StringType(max_length=255, min_length=1)
    road_end = StringType(max_length=255, min_length=1)

    section_order = IntType()

    province = StringType(max_length=255, min_length=1)
    district = StringType(max_length=255, min_length=1)
    # province = ForeignKey('administrations.AdminUnit', null=True,
    #                              blank=True, on_delete=PROTECT,
    #                              related_name='province_sections')
    # district = ForeignKey('administrations.AdminUnit', null=True,
    #                              blank=True, on_delete=PROTECT,
    #                              related_name='district_sections')

    commune = StringType(max_length=25)
    management = IntType()

    start_km = FloatType()
    end_km = FloatType()
    length = FloatType(required=True)
    vpromms_length = FloatType()
    lanes = IntType(default=0)
    width = FloatType(default=0)
    road_class = IntType(default=0)
    terrain = IntType(default=0)
    temperature = IntType(default=0)
    moisture = IntType(default=0)
    road_type = IntType(default=0)
    surface_type = IntType(default=0)
    condition_class = IntType(default=0)
    roughness = FloatType(default=0)
    traffic_level = IntType(default=0)
    traffic_growth = IntType(default=0)
    structural_no = FloatType(default=0)
    pavement_age = IntType(default=0)

    aadt_motorcyle = FloatType(default=0.0)
    aadt_carsmall = FloatType(default=0.0)
    aadt_carmedium = FloatType(default=0.0)
    aadt_delivery = FloatType(default=0.0)
    aadt_4wheel = FloatType(default=0.0)
    aadt_smalltruck = FloatType(default=0.0)
    aadt_mediumtruck = FloatType(default=0.0)
    aadt_largetruck = FloatType(default=0.0)
    aadt_articulatedtruck = FloatType(default=0.0)
    aadt_smallbus = FloatType(default=0.0)
    aadt_mediumbus = FloatType(default=0.0)
    aadt_largebus = FloatType(default=0.0)
    aadt_total = FloatType(default=0.0)

    def __str__(self):
        return str(self.to_primitive())

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return Section(json.load(f))

    @staticmethod
    def maybe_int(maybe_int: Optional[int]):
        return int(maybe_int) if maybe_int else 0.0

    @staticmethod
    def maybe_float(maybe_float: Optional[float]):
        return float(maybe_float) if maybe_float else 0.0

    @classmethod
    def from_row(cls, row):
        in_data = {
            "orma_way_id": row["way_id_district"],
            "section_id": row["way_id_district"],
            "road_number": row["road number"],
            "road_name": row["name"],
            "road_start": row["road start location"],
            "road_end": row["road end location"],
            "province": row["province"],
            "district": row["district"],
            "commune": row["section_commune_gso"],
            "management": Section.maybe_int(row["management"]),
            # "start_km": float(row["Start_Km"]),
            # "end_km": float(row["End_Km"]),
            "length": row["length"],
            "lanes": Section.maybe_int(row["section_lanes"]),
            "width": 6.0 if row["width"] == "6+" else Section.maybe_float(row["width"]),
            "road_class": row["link_class"],
            "terrain": row["section_terrain"],
            "temperature": row["section_temperature"],
            "moisture": row["section_moisture"],
            "surface_type": row["section_surface"],
            "condition_class": row["condition"],
            "roughness": Section.maybe_float(row["iri"]),
            "traffic_level": row["section_traffic"],
            "traffic_growth": row["section_traffic_growth"],
            "pavement_age": Section.maybe_int(row["section_pavement_age"]),
            "aadt_motorcyle": Section.maybe_int(row["section_motorcycle"]),
            "aadt_carsmall": Section.maybe_int(row["section_small_car"]),
            "aadt_carmedium": Section.maybe_int(row["section_medium_car"]),
            "aadt_delivery": Section.maybe_int(row["section_delivery_vehicle"]),
            "aadt_4wheel": Section.maybe_int(row["section_four_wheel"]),
            "aadt_smalltruck": Section.maybe_int(row["section_light_truck"]),
            "aadt_mediumtruck": Section.maybe_int(row["section_medium_truck"]),
            "aadt_largetruck": Section.maybe_int(row["section_heavy_truck"]),
            "aadt_articulatedtruck": Section.maybe_int(row["section_articulated_truck"]),
            "aadt_smallbus": Section.maybe_int(row["section_small_bus"]),
            "aadt_mediumbus": Section.maybe_int(row["section_medium_bus"]),
            "aadt_largebus": Section.maybe_int(row["section_large_bus"]),
            "aadt_total": Section.maybe_int(row["aadt"]),
        }
        try:
            return Section(in_data)
        except Exception as err:
            return InvalidSection(err, in_data)

    def to_dict(self):
        return {
            "orma_way_id": self.id,
            "section_id": self.section_id,
            "road_number": self.road_number,
            "road_name": self.road_name,
            "road_start": self.road_start,
            "road_end": self.road_end,
            "province": self.province,
            "district": self.district,
            "commune": self.commune,
            "management": self.management,
            "road_length": self.length,
            "lanes": self.lanes,
            "width": self.width,
            "road_class": self.road_class,
            "terrain": self.terrain,
            "temperature": self.temperature,
            "moisture": self.moisture,
            "surface_type": self.surface_type,
            "condition_class": self.condition_class,
            "roughness": self.roughness,
            "pavement_age": self.pavement_age,
            "aadt_total": self.aadt_total,
        }

    def set_aadts(self, aadts: List[float]):
        (
            self.aadt_motorcyle,
            self.aadt_carsmall,
            self.aadt_carmedium,
            self.aadt_delivery,
            self.aadt_4wheel,
            self.aadt_smalltruck,
            self.aadt_mediumtruck,
            self.aadt_largetruck,
            self.aadt_articulatedtruck,
            self.aadt_smallbus,
            self.aadt_mediumbus,
            self.aadt_largebus,
        ) = aadts

    def get_aadts(self):
        return (
            self.aadt_motorcyle,
            self.aadt_carsmall,
            self.aadt_carmedium,
            self.aadt_delivery,
            self.aadt_4wheel,
            self.aadt_smalltruck,
            self.aadt_mediumtruck,
            self.aadt_largetruck,
            self.aadt_articulatedtruck,
            self.aadt_smallbus,
            self.aadt_mediumbus,
            self.aadt_largebus,
        )

    REQUIRED_FIELDS = ["lanes", "width"]

    def invalid_reason(self):
        errors = []
        if is_missing(self.road_type) and is_missing(self.surface_type):
            errors.append("Must define either road type or road surface type")
        if is_missing(self.width) and is_missing(self.lanes):
            errors.append("Must define either road width or number of lanes")
        if is_missing(self.roughness) and is_missing(self.condition_class):
            errors.append("Must define either roughness or road condition")
        if is_missing(self.traffic_level) and is_missing(self.aadt_total):
            errors.append("Must define either aadt_total or traffic_level")
        if is_missing(self.terrain):
            errors.append("No terrain data")
        return errors if errors else None


def is_missing(val):
    return val is None or val == 0
