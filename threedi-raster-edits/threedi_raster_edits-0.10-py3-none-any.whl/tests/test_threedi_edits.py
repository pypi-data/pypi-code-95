# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 16:02:59 2021

@author: chris

#TODO
    - Add a node
    - Add a manhole
    - Add a channel
#DONE
    - Read a sqlite
    - Create empty sqlite
    - Read rasters
    - Add rasters
    - Write sqlite
    - Write sqlite + Rasters

"""
# First-party imports
import os
import pathlib

# Third-party imports
import logging

logger = logging.getLogger()

# Local imports
from threedi_raster_edits.threedi.edits import ThreediEdits
from threedi_raster_edits.threedi.tables.templates import Templates

# from threedi_raster_edits.gis.raster import Raster
from threedi_raster_edits.gis.point import Point
from threedi_raster_edits.threedi.utils.exceptions import ThreediValueTypeError

# Globals
# __file__ = "C:/Users/chris.kerklaan/Documents/Github/threedi-raster-edits/threedi_raster_edits/tests/test_threedi_edits.py"

TEST_DIRECTORY = pathlib.Path(__file__).parent / "data" / "threedi_edits"

DEM_PATH = TEST_DIRECTORY / "dem.tif"
BWN_PATH = TEST_DIRECTORY / "bwn" / "bwn_test.sqlite"


def test_create_empty_model():
    """tests if an empty model can be created"""
    model = ThreediEdits.from_scratch()
    model.write(TEST_DIRECTORY / "empty.sqlite")


def test_read_sqlite():
    model = ThreediEdits(TEST_DIRECTORY / "empty.sqlite")
    assert type(model) == ThreediEdits


# failing in build_and_test - github
# def test_add_rasters_placed():
#     """adds a raster, placed"""
#     model = ThreediEdits.from_scratch()
#     global_settings = model.global_settings
#     numerical_settings = model.numerical_settings
#     simple_infiltration = model.simple_infiltration

#     template = Templates()
#     gs = template.global_setting
#     gs["dem_file"] = "rasters/dem.tif"
#     global_settings.add(gs)

#     ns = template.numerical_setting
#     numerical_settings.add(ns)

#     si = template.simple_infiltration
#     simple_infiltration.add(si)

#     dem = Raster(DEM_PATH)
#     model.dem = dem

#     model.write(TEST_DIRECTORY / "test_write" / "empty.sqlite", rasters=True)

#     assert os.path.exists(str(TEST_DIRECTORY / "test_write" / "empty.sqlite"))


def test_write_existing_raster():
    """tests if existing rasters can be loaded and written"""
    model = ThreediEdits(BWN_PATH)
    model.write(TEST_DIRECTORY / "test_write_raster" / "empty.sqlite", rasters=True)
    assert os.path.exists(str(TEST_DIRECTORY / "test_write_raster" / "empty.sqlite"))
    assert os.path.exists(
        str(TEST_DIRECTORY / "test_write_raster" / "rasters" / "dem_hoekje.tif")
    )
    assert os.path.exists(
        str(TEST_DIRECTORY / "test_write_raster" / "rasters" / "storage_glg_hoekje.tif")
    )


def test_add_connection_node():
    """tests if a connection node can be added"""
    model = ThreediEdits(BWN_PATH)
    nodes = model.nodes
    template = Templates()
    node = template.node
    node["code"] = "test-node"
    node["the_geom"] = Point.from_point((51.1, 4.3))
    nodes.add(node)
    assert nodes.count == 73
    assert nodes[74]["code"] == "test-node"


def test_add_connection_node_wo_code():
    """tests if a connection node cannot be added wo code"""
    model = ThreediEdits(BWN_PATH)
    nodes = model.nodes
    template = Templates()
    node = template.node
    node["the_geom"] = Point.from_point((51.1, 4.3))
    try:
        nodes.add(node)
    except ThreediValueTypeError:
        assert True
    else:
        assert False


def test_node_sampling():
    """tests if connection nodes can be sampled on a dem"""

    model = ThreediEdits(BWN_PATH)
    heights = model.nodes_height()

    assert heights[435] == 10.0
    assert model.dem.epsg == 28992


def test_node_view():
    """tests if node view is working"""
    model = ThreediEdits(BWN_PATH)
    view = model.node_view
    assert view[483]["v2_weir_start"]["display_name"] == "KST-JL-2069"


def test_node_delete():
    model = ThreediEdits(BWN_PATH)
    model.delete_node(483)
    assert 483 not in model.nodes.fids
