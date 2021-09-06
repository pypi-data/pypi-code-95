# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 10:54:38 2021

@author: chris.kerklaan

Functions to test:
#TODO

    
#Done:
    # loading
    - load path
    - load ogr_ds
    - load ogr_postgres
    
    # load index
    - Load index
    
    # load table
    - load table
    
    # Spatial filtering
    - intersect
    - within
    - layer fitler
    
    # Table filtering
    - Single filter
    - Double filter
    
    # add feature
    - add feature
    - add feature with index
    - add feature with table
    
    # delete feature
    - delete feature
    - delete feature with index
    - delete feature with table
    
    # fields
    - Add field
    - Delete field
    
    # functions
    - rasterize
    - clip 
    - dissolve
    - difference
    - reproject
    - multipart2singlepart
    - centroid
    - simplify

    # dependecies
    - Depedency without rtree

    
"""
# First-party imports
# import os
import pathlib

# Third-party imports
import numpy as np
from osgeo import ogr

# Local imports
from threedi_raster_edits.gis.vector import Vector
from threedi_raster_edits import Raster
from threedi_raster_edits.gis.feature import Feature

# Globals
# __file__ = "C:/Users/chris.kerklaan/Documents/Github/threedi-raster-edits/threedi_raster_edits/tests/test_gis_vector.py"
TEST_DIRECTORY = str(pathlib.Path(__file__).parent.absolute()) + "/data/gis_vector/"


def test_load_path():
    """tests if vector is correctly loaded using a path"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    assert lines.count > 0
    lines.close()


def test_load_ds():
    """tests if vector is correctly loaded using an ogr datasource"""
    lines_ds = ogr.Open(TEST_DIRECTORY + "lines.shp")
    lines = Vector.from_ds(lines_ds)
    assert lines.count > 0
    lines.close()


def test_fix_multisurfaces():
    """tests if multisurfaces are fixed"""
    bgt = Vector(TEST_DIRECTORY + "bgt_panden.gpkg", layer_name="bgt_panden")
    fixed = bgt.fix(geometry_type=ogr.wkbMultiPolygon)
    assert fixed.geometry_type == ogr.wkbMultiPolygon
    assert fixed[0].geometry.type == ogr.wkbMultiPolygon


# def test_load_pg():
#     """ tests if vector is correctly loaded using a postgres ds"""
#     pg_test = Vector.from_pg(
#         host="localhost",
#         port=5432,
#         password="postgres",
#         user="postgres",
#         dbname="postgres",
#         layer_name="buurten",
#     )
#     assert pg_test.count > 0
#     pg_test.close()


def test_load_scratch():
    """tests if vector can be created from scratch"""
    multi = Vector.from_scratch("temp", ogr.wkbMultiPolygon, 28992)
    assert isinstance(multi, Vector)


def test_load_index():
    """checks if index is loaded, count and bounds"""
    lines = Vector(TEST_DIRECTORY + "lines.shp", create_index=True)
    lines = lines.copy()
    assert lines.idx.get_size() == lines.count
    assert lines.idx.bounds == [
        117366.7415368543,
        117647.1103333626,
        459623.5067579962,
        459774.68880537077,
    ]


def test_load_table():
    """checks if table is correclty loaded in term of size and keys"""
    lines = Vector(TEST_DIRECTORY + "lines.shp", create_table=True)
    lines = lines.copy()
    assert lines.fields.names[0] in lines.table.keys()
    assert len(lines.table["HOID"]) == lines.count


def test_spatial_filtering():
    """tests spatial filtering on witin and intersect, with and without layer filter"""

    lines = Vector(TEST_DIRECTORY + "lines.shp", create_index=True)
    lines = lines.copy()

    geometry = Vector(TEST_DIRECTORY + "geometry.shp")[0].geometry

    fids = lines.spatial_filter(geometry, method="intersect")
    assert len(fids) == 21

    fids = lines.spatial_filter(geometry, method="intersect", filter=True)
    assert len(fids) == 21

    fids = lines.spatial_filter(geometry, method="within")
    assert len(fids) == 14

    fids = lines.spatial_filter(geometry, method="within", filter=True)
    assert len(fids) == 14


def test_table_filter():
    """tests on table filtering
    1. Single filter
    2. double filter
    3. Feature output
    4. fid output
    """

    lines = Vector(TEST_DIRECTORY + "lines.shp", create_table=True)
    lines = lines.copy()
    assert len(lines.filter(HOID="44466")) == 15
    assert len(lines.filter(HOID="44466", test_field=2)) == 1
    assert type(lines.filter(test_field=2, return_fid=True)[0]) == int
    assert type(lines.filter(test_field=2)[0]) == Feature


def test_add_feature():
    """tests if a feature is correctly added by using a feature,
    a dictionary and a geometry
    """

    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    single = Vector(TEST_DIRECTORY + "single.shp")

    lines.add(single[0])
    assert lines.count == 90
    assert lines[90].items["test_field"] == 1


def test_add_feature_w_index():
    """tests if a feature is correctly added by using a feature w index"""

    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    single = Vector(TEST_DIRECTORY + "single.shp")

    lines.set_index()
    lines.add(single[0])
    assert lines.idx.get_size() == 90
    assert lines.idx.bounds == [
        117366.7415368543,
        117647.1103333626,
        459623.5067579962,
        459774.68880537077,
    ]


def test_add_feature_w_table():
    """tests if a feature is correctly added by using a feature,
    a dictionary and a geometry
    """

    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()

    single = Vector(TEST_DIRECTORY + "single.shp")
    lines.set_table()
    lines.add(single[0], update_table=True)
    assert len(lines.table["fid"]) == 90
    assert lines.table["HOID"][-1] == "47161"


def test_delete_feature():
    """tests if feature is properly deleted"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.delete(0)
    assert lines.count == 88


def test_delete_feature_w_index():
    """tests if feature is properly deleted with index"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.set_index()
    lines.delete(0)
    assert lines.idx.get_size() == 88


def test_delete_feature_w_table():
    """tests if feature is properly deleted with table"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.set_table()
    lines.delete(0)
    assert len(lines.table["fid"]) == 88


def test_copy():
    """tests if features are copied"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    copy = lines.copy()
    assert lines.settings == copy.settings
    assert lines.count == copy.count
    assert lines[10].items == copy[10].items


def test_copy_shell():
    """tests if they have no count"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    copy = lines.copy(shell=True)
    assert lines.settings == copy.settings
    assert copy.count == 0


def test_add_field():
    """tests if field is added and if one can add something"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.add_field("x", float)
    assert "x" in lines.fields.items

    lines.add(items={"x": 1.0})
    assert lines[90].items["x"] == 1


def test_delete_field():
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.delete_field("test_field")
    assert "test_field" not in lines.fields.items
    assert "test_field" not in lines[80].items


def test_write_shape():
    """tests if a shape can be written"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.write(TEST_DIRECTORY + "lines_write.shp", overwrite=True)
    lines2 = Vector(TEST_DIRECTORY + "lines_write.shp")
    assert lines.count == lines2.count
    assert lines[0].items == lines2[0].items
    assert lines[0].geometry.wkt == lines2[0].geometry.wkt
    lines.close()


def test_write_gpkg():
    """tests if a geopackage can be written"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    lines = lines.copy()
    lines.write(TEST_DIRECTORY + "lines_write.gpkg", overwrite=True)
    lines2 = Vector(TEST_DIRECTORY + "lines_write.gpkg")
    assert lines.count == lines2.count
    assert lines[0].items == lines2[1].items
    assert lines[0].geometry.wkt == lines2[1].geometry.wkt
    lines.close()


# def test_pg_upload():
#     """ tests if a vector can be uploaded to postgres"""

#     lines = Vector(TEST_DIRECTORY + "lines.shp")
#     lines.pgupload(
#         host="localhost",
#         port=5432,
#         password="postgres",
#         user="postgres",
#         dbname="postgres",
#         layer_name="lines",
#     )
#     lines.close()

#     lines = Vector(TEST_DIRECTORY + "lines.shp")
#     lines2 = Vector.from_pg(
#         host="localhost",
#         port=5432,
#         password="postgres",
#         user="postgres",
#         dbname="postgres",
#         layer_name="lines",
#     )
#     assert lines.count == lines.count
#     assert lines[0]["HOID"] == lines2[1]["hoid"]

#     # not equal due to forcing of geomtries
#     # self.assertTrue(
#     #     lines[0].geometry.wkt == lines2[1].geometry.wkt, "Geometry is not equal"
#     # )
#     lines2.close()
#     lines.close()
#     lines = Vector(TEST_DIRECTORY + "lines.shp")


def test_rasterize_ones():
    """tests rasterization based on counts of array using field"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    geotransform = (117366.7415, 1.0, 0.0, 459774.6888, 0.0, -1.0)
    rows = 151
    columns = 280
    array = lines.rasterize(rows, columns, geotransform)
    array[array == -9999] = np.nan
    assert np.nansum(array) == 1757.0
    lines.close()


def test_rasterize_fields():
    """tests rasterization based on counts of array using field"""

    lines = Vector(TEST_DIRECTORY + "lines.shp")
    geotransform = (117366.7415, 1.0, 0.0, 459774.6888, 0.0, -1.0)
    rows = 151
    columns = 280
    array = lines.rasterize(rows, columns, geotransform, field="test_field")
    array[array == -9999] = np.nan
    assert np.nansum(array) == 1778.0
    lines.close()


def test_buffer():
    """tests if buffer algorithm is performed correctly"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    buffered = lines.buffer(10, quiet=True)
    assert buffered[0].geometry.area > 0
    lines.close()
    buffered.close()


def test_simplify():
    """tests if simplify algorithm is performed correctly"""
    shape = Vector(TEST_DIRECTORY + "strange_shape.shp")
    simplified = shape.simplify(10)
    assert simplified[0].geometry.wkb_size < shape[0].geometry.wkb_size


def test_centroid():
    """tests if simplify algorithm is performed correctly"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    centroids = lines.centroid()

    original = lines[0].geometry.Centroid().ExportToWkt()
    new = centroids[0].geometry.centroid.wkt
    assert original == new


def test_multipart_to_singlepart():
    """tests if multipart to singlepart on geometry type and counts"""
    multi = Vector(TEST_DIRECTORY + "multi.shp")
    singles = multi.to_single()
    assert singles.geometry_type == 3
    assert singles.count == 2
    assert singles[0].geometry.type == 3


def test_reproject():
    """tests if reprojects has a new bbox, epsg is changed and geometry has changed"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    new_lines = lines.reproject(4326)
    assert max(new_lines.extent) < 60
    assert new_lines[0].geometry.points[0][0] < 60


def test_clip():
    """tests if a clip works by count and feature geometry"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    mask = Vector(TEST_DIRECTORY + "geometry.shp")
    clipped = lines.clip(mask)
    assert clipped.count == 21

    feat_13 = "LINESTRING (117556.454477141 459720.712475407,117576.403681566 459722.13699034)"
    assert clipped[14].geometry.wkt == feat_13


def test_difference():
    """tests if a difference works by count and feature geometry"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    mask = Vector(TEST_DIRECTORY + "geometry.shp")
    differenced = lines.difference(mask)
    assert differenced.count == 75
    feat_51 = "LINESTRING (117575.529616571 459712.808025775,117577.996659787 459713.235393432)"
    assert differenced[52].geometry.wkt == feat_51


def test_dissolve():
    """tests if a difference works by count and wkbsize"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    dissolved = lines.dissolve()
    assert dissolved.count == 1
    assert dissolved[0].geometry.wkb_size == 3617
    assert dissolved[0].geometry.type == ogr.wkbMultiLineString


def test_dissolve_field():
    """tests if a difference works by count and wkbsize"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    dissolved = lines.dissolve(field="HOID")
    assert dissolved.count == 9
    assert dissolved[0].geometry.wkb_size == 91


def test_polygon_to_lines():
    """tests polygon to lines"""
    geometry = Vector(TEST_DIRECTORY + "geometry.shp")
    lines = geometry.polygon_to_lines()
    assert lines.geometry_type == 2
    assert lines[0].geometry.type == 2


def test_rtree_dependecy_spatial_filter():
    """tests if spatial filter works without rtree"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    geometry = Vector(TEST_DIRECTORY + "geometry.shp")
    lines.has_rtree = False
    fids = lines.spatial_filter(geometry[0].geometry)
    assert len(fids) == 21


def test_rtree_dependecy_difference():
    """tests if difference works without rtree"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    geometry = Vector(TEST_DIRECTORY + "geometry.shp")
    lines.has_rtree = False
    differences = lines.difference(geometry)
    assert differences.count == 75


def test_rtree_dependecy_clip():
    """tests if clip works without rtree"""
    lines = Vector(TEST_DIRECTORY + "lines.shp")
    geometry = Vector(TEST_DIRECTORY + "geometry.shp")
    lines.has_rtree = False
    clip = lines.clip(geometry, quiet=False)
    assert clip.count == 21


def test_integrated_delete_dissolve():
    """tests if integrated works after polygonizing, looping, deleting and getting count
    problem:
        python crashes when this used to be done.

    """
    lines_raster = Raster(TEST_DIRECTORY + "lines.tif")
    lines_vector_path = lines_raster.polygonize(quiet=True)
    lines_vector = Vector(lines_vector_path)
    count = lines_vector.count

    for i, feature in enumerate(lines_vector):
        if i == 1:
            lines_vector.delete(feature.fid)
    assert lines_vector.count == count - 1

    dissolved = lines_vector.dissolve()
    single_dissolved = dissolved.to_single()
    assert single_dissolved.count == count - 1
