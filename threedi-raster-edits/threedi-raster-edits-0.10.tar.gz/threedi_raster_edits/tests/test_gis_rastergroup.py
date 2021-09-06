# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 11:38:51 2021

@author: chris.kerklaan


Script for automated testing of the raster group object

#TODO functions:
    0. other
Currently supported functions
    1. Check alignment
        1. Data/nodata value
        2. geotransform
        3. rows, columns
        
    

"""
# First-party imports
import glob
import pathlib

# Third-party imports
import numpy as np

# Local imports
from threedi_raster_edits.gis.raster import Raster
from threedi_raster_edits.gis.rastergroup import RasterGroup

# Globals
TEST_DIRECTORY = (
    str(pathlib.Path(__file__).parent.absolute()) + "/data/gis_raster_group/"
)
# TEST_DIRECTORY = "//utr-3fs-01.nens.local/WorkDir/C_Kerklaan/scripts/base/tests/input/gis_raster_group/"


RASTERS = []
for raster_path in glob.glob(TEST_DIRECTORY + "*.tif"):
    raster = Raster(raster_path)
    raster.load_to_memory()
    RASTERS.append(raster)


def test_check_alignment_geotransform():
    """Tests is alignment checking notices geotransform changes"""
    test_rasters = [raster.copy() for raster in RASTERS]
    test_rasters[1].geotransform = (96798.0, 0.5, 0.0, 417515.0, 0.0, -0.5)
    rastergroup = RasterGroup(test_rasters)

    output = rastergroup.check_alignment()
    assert len(output["errors"]) > 0


def test_check_alignment_rows_columns():
    """Tests is alignment checking notices rows/columns changes"""
    test_rasters = [raster.copy() for raster in RASTERS]
    test_rasters.append(test_rasters[1].empty_copy(rows=1, columns=1))
    rastergroup = RasterGroup(test_rasters)

    output = rastergroup.check_alignment()
    assert len(output["errors"]) > 0


def test_check_alignment_data_nodata():
    """Tests is alignment checking notices data/nodata changes"""
    test_rasters = [raster.copy() for raster in RASTERS]
    array = test_rasters[2].array

    array[array > 0] = np.nan
    test_rasters[2].array = array
    test_rasters[2].name = "Test raster"
    rastergroup = RasterGroup(test_rasters)

    output = rastergroup.check_alignment()
    errors_present = len(output["errors"]) > 0
    assert errors_present

    if errors_present:
        assert "counts" in output["errors"][0]
