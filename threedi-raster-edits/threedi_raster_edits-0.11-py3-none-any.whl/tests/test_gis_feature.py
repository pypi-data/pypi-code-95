# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 18:53:32 2021

@author: chris.kerklaan
"""
# First-party imports
import pathlib

# Third-party imports
# import numpy as np
# from osgeo import ogr

# Local imports
from threedi_raster_edits.gis.vector import Vector

# from threedi_raster_edits.gis.feature import Feature

# Globals
TEST_DIRECTORY = str(pathlib.Path(__file__).parent.absolute()) + "/data/gis_feature/"


def test_set_feature():
    """tests if feature has been set after field is added"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.add_field("test", float)

    lines[0]["test"] = 0.1

    assert lines[0]["test"] == 0.1
    lines = None
