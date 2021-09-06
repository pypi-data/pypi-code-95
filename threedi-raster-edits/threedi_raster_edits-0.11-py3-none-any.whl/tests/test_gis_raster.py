# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:56:02 2021

@author: chris.kerklaan

Script for automated testing of the raster object

#TODO functions:
    
Currently supported functions
    1. test_tiling_blocksize
    2. test_tiling_blocksize_optimization
    3. test_merge (used in tiling)
    4. test_tiling (testing changes)
    5. test_push_vector_field
    6. test_push_vector_value
    7. test_push_vector_set_to_nodata
    8. test_empty_copy
    9. align
    10. clip
    11. resample
    12. reproject
    13. idw
    14. polygonize (float)
    15. classify
    
"""

# First-party imports
import pathlib

# Third-party imports
import numpy as np

# Local imports
from threedi_raster_edits.gis.raster import Raster
from threedi_raster_edits.gis.raster import Vector
from threedi_raster_edits.gis.rastergroup import RasterGroup

# Globals
TEST_DIRECTORY = str(pathlib.Path(__file__).parent.absolute()) + "/data/gis_raster/"
RASTER = Raster(TEST_DIRECTORY + "crop.tif")
VECTOR = Vector(TEST_DIRECTORY + "polygon.shp")
RASTER_TEMPLATE = Raster(TEST_DIRECTORY + "template.tif")


def test_tiling_blocksize():

    RASTER.optimize_blocksize = False
    RASTER.blocksize = 256
    tiles = [tile for tile in RASTER]

    # total tiles --> only works if the same input is used
    assert len(tiles) == 15

    # First tile
    for tile in RASTER:
        break
    assert tile.size == 256 * 256


def test_tiling_blocksize_optimization():
    """optimization is standard on"""
    RASTER.optimize_blocksize = True
    tiles = [tile for tile in RASTER]

    # total tiles --> only works if the same input is used
    assert len(tiles) == 1


def test_tiling():
    """testing addition in tiling"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.optimize_blocksize = False
    raster.blocksize = 256
    target = raster.copy(shell=True)
    for tile in raster:
        array = tile.array
        tile.array = array + 1
        target.array = array, *tile.location

    assert np.nansum(target.array) == 2803996.0
    target = None


def test_push_vector_value():
    """tests push vector with a value"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.optimize_blocksize = True
    pushed_raster = raster.push_vector(VECTOR, value=100)
    assert np.nansum(pushed_raster.array) == 2863532.0
    raster = None


def test_push_vector_field():
    """tests push vector when set to field"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    pushed_raster = raster.push_vector(VECTOR, field="test")
    assert np.nansum(pushed_raster.array) == 2807372.0
    raster = None


def test_push_vector_nodata():
    """tests push vector when set to nodata"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    pushed_raster = raster.push_vector(VECTOR, set_to_nodata=True)
    assert np.nansum(pushed_raster.array) == 2801132.0
    raster = None


def test_copy_shell():
    """tests an emtpy copy, should retrieve a copy of the raster without anything"""
    copy = RASTER.copy(shell=True)

    # array should be 0
    assert np.nansum(copy.array) == 0.0, "Array of empty copy is not 0"

    # check settigns
    assert copy.geotransform == RASTER.geotransform

    # check settigns
    assert copy.nodata_value == RASTER.nodata_value

    # check settigns
    assert copy.spatial_reference.wkt == RASTER.spatial_reference.wkt


def test_too_large_raster():
    """Tests if a too large raster is properly aligned"""

    raster_path = TEST_DIRECTORY + "template_larger.tif"
    raster = Raster(raster_path)
    group = RasterGroup([raster, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) > 0

    aligned = raster.align(RASTER_TEMPLATE, nodata_align=False, fill_value=None)

    group = RasterGroup([aligned, RASTER_TEMPLATE])
    checks = group.check_alignment()

    # Failure can be present in counts, but that's okay due to nodata_align=False
    others = all([False for error in checks["errors"] if error[0] != "counts"])
    assert others


def test_too_small_raster():
    """Tests if a too small raster is properly aligned"""

    raster_path = TEST_DIRECTORY + "template_smaller.tif"
    raster = Raster(raster_path)
    group = RasterGroup([raster, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) > 0

    aligned = raster.align(RASTER_TEMPLATE, nodata_align=False, fill_value=None)

    group = RasterGroup([aligned, RASTER_TEMPLATE])
    checks = group.check_alignment()

    # Failure can be present in counts, but that's okay due to nodata_align=False
    other = all([False for error in checks["errors"] if error[0] != "counts"])
    assert other


def test_raster_w_too_much_nodata():
    """tests if a raster with too much nodata is properly aligned"""
    raster_path = TEST_DIRECTORY + "template_w_nodata.tif"
    raster = Raster(raster_path)
    group = RasterGroup([raster, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) > 0

    aligned = raster.align(RASTER_TEMPLATE, nodata_align=True, fill_value=100)

    group = RasterGroup([aligned, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) == 0


def test_raster_w_too_little_nodata():
    """tests if a raster with too little nodata is properly aligned"""
    raster_path = TEST_DIRECTORY + "template_wo_nodata.tif"
    raster = Raster(raster_path)
    group = RasterGroup([raster, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) > 0

    aligned = raster.align(RASTER_TEMPLATE, nodata_align=True, fill_value=100)

    group = RasterGroup([aligned, RASTER_TEMPLATE])
    checks = group.check_alignment()

    assert len(checks["errors"]) == 0


def test_clip():
    """test if a clip is correct"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    vector = Vector(TEST_DIRECTORY + "polygon.shp")
    clipped = raster.clip(vector)
    assert np.nansum(clipped.array) == 2856
    raster.close()
    clipped.close()


def test_reproject():
    """tests reproject by geotransform and epsg"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.reproject(4326, quiet=False)

    # check epsg
    assert raster.spatial_reference.epsg == 4326, "incorrect epsg"

    # check geotransofrm
    assert raster.geotransform[0] < 1000


def test_resample():
    """tests if resample works"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.resample(1, 1, quiet=False)
    assert raster.size == 188340
    assert raster.geotransform[1] == 1.0
    assert raster.geotransform[5] == -1.0


def test_fill_nodata():
    """tests if count of idw result"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    edit = raster.copy()
    array = edit.array
    array[array == 8] = raster.nodata_value
    edit.array = array
    idw = edit.fill_nodata(max_iterations=1)
    assert np.nansum(idw.array) == 351146.0


def test_replace_nodata():
    """tests if nodata value of raster is replaced"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    is_nodata = ~raster.mask
    raster.replace_nodata(-8888)
    assert raster.nodata_value == -8888

    array = raster.band.ReadAsArray()
    assert (is_nodata == (array == -8888)).all()


def test_polygonize_integer():
    """tests if polygonize works"""
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.change_data_type(int)
    vector = Vector.from_mem_path(raster.polygonize())
    vector.set_table()
    assert vector.table["dn"][0] == 8
    assert type(vector.table["dn"][0]) == int
    assert vector.count == 386


def test_polygonize_float():
    raster = Raster(TEST_DIRECTORY + "crop.tif")
    raster.change_data_type(float)
    vector = Vector.from_mem_path(raster.polygonize())
    vector.set_table()

    assert vector.table["dn"][0] == 8
    assert type(vector.table["dn"][0]) == float
    assert vector.count == 386
