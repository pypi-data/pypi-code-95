# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:58:57 2021

@author: chris.kerklaan

A feature wrapper for threedi models

Here, all the checks are done.
Checks consist of:
    1. Value Type checking # implemented
    2. Value Logical checking # Not implemented
    3. Value connected checks #TODO --> This is done in vector_group
    


"""
# system imports
import logging

# Third-party import
import warnings

# Local imports
from threedi_raster_edits.gis.feature import Feature
from threedi_raster_edits.gis.geometries import convert_geometry
from threedi_raster_edits.gis.fields import OGR_TYPES_INVERT
from threedi_raster_edits.threedi.tables.constants import Properties
from threedi_raster_edits.threedi.utils.exceptions import ThreediValueTypeError
from threedi_raster_edits.threedi.utils.exceptions import (
    ThreediValueTypeWarning,
)
from threedi_raster_edits.threedi.utils.exceptions import _HAPPY
from threedi_raster_edits.threedi.utils.exceptions import custom_formatwarning


# Globals
PROPERTIES = Properties()
warnings.formatwarning = custom_formatwarning


logger = logging.getLogger(__name__)


class ThreediFeature(Feature):
    def __init__(
        self,
        feature,
        layer,
        table_name,
        properties,
        set_feature=True,
        custom_set_function=None,
        checks=True,
    ):
        Feature.__init__(self, feature, layer)
        self.properties = properties
        self.table_name = table_name
        self.set_feature = set_feature
        self.custom_set_function = custom_set_function
        self.check = True

    def __str__(self):
        return f"3Di row, items: {self.all_items}"

    def __repr__(self):
        return f"3Di row, items: {self.all_items}"

    def set_output_type(self, key, value):
        self.output_type = OGR_TYPES_INVERT[self.properties[key]["type"]]

    def set_geometry(self, geometry):
        """sets and converts the geometry"""

        geometry = convert_geometry(geometry)

        # self.ptr.SetGeomField(self.geometry_fields.translate['the_geom'], geometry)

        if "the_geom" in self.geometry_fields.items:
            self.ptr.SetGeomField(self.geometry_fields.translate["the_geom"], geometry)
        else:
            self.ptr.SetGeometry(geometry)

        if self.set_feature:
            self.layer.SetFeature(self.ptr)

    def check_type(self, key, value, try_change=True):
        """does None type check and type check, returns ValueError if incorrect"""

        # first do type check
        if value == None:
            if self.properties[key]["optional"] == True:  # none allowed
                return value
            else:
                raise ThreediValueTypeError(
                    "Value None is not allowed here",
                    self.table_name,
                    key,
                    value,
                )

        else:
            type_value = type(value)
            correct_type = self.output_type == type(value)
            if not correct_type:
                logger.debug(
                    ThreediValueTypeWarning(
                        f"incorrect type, trying to correct {type_value} to {self.output_type}",
                        self.table_name,
                        key,
                        value,
                    )
                )
                try:
                    if self.output_type == bool:
                        value = int(value)
                    value = self.output_type(value)
                except Exception:
                    raise ThreediValueTypeError(
                        f"""Found incorrect type of {type_value} where  {self.output_type} is expected""",
                        self.table_name,
                        key,
                        value,
                    )
                else:
                    logger.debug(
                        ThreediValueTypeWarning(
                            f"{_HAPPY}, corrected input to {type(value)}: {value}",
                            self.table_name,
                            key,
                            value,
                        )
                    )
                    return value
            else:
                return value

    def set_routine(self, key, value):
        """general routine/helper for __setitem__,
        specific routines are added in the models themselves"""

        # set the geometry
        if key == "geometry" or key == "the_geom":
            self.set_geometry(value)
            return

        # check the output type
        if self.check:
            self.set_output_type(key, value)
            value = self.check_type(key, value)

        self.ptr.SetField(key, value)
        if self.set_feature:
            self.layer.SetFeature(self.ptr)

    def __setitem__(self, key, value):
        """setitem uses a function which is define by the model below"""
        if self.custom_set_function:
            key, value = self.custom_set_function(key, value)
        self.set_routine(key, value)
