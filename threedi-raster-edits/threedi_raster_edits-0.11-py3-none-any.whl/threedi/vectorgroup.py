# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:52:16 2021

@author: chris.kerklaan

#TODO:
    CHECKS:
        1. check connected tables

    
"""
# First-party imports
import shutil
import pathlib
import logging

# Third-party imports
from osgeo import ogr
from osgeo import osr

# Local imports
from threedi_raster_edits.threedi.tables.constants import TABLES, Properties
from threedi_raster_edits.threedi.tables.models import MODEL_MAPPING
from threedi_raster_edits.threedi.utils.exceptions import (
    ThreediConnectedTableError,
)
from threedi_raster_edits.gis.vectorgroup import VectorGroup
from threedi_raster_edits.gis.vector import Vector

# Globals
OGR_SQLITE_DRIVER = ogr.GetDriverByName("SQLite")
EMPTY_SQLITE_PATH = str(pathlib.Path(__file__).parent.absolute()) + "/data/empty.sqlite"
logger = logging.getLogger(__name__)


class ThreediVectorGroup(VectorGroup):
    """ThreediVectorGroup's base is always made up from  constants fields
    if a new 'sqlite' gets added it will always be transfered to the in memory object
    params:
        ogr_ds: ogr.DataSource
        mode:
            'write': Used to write a file
            'empty': Returns an empty in-mem ogr threedi model
            'copy': Used when a full threedimodel is presented


    """

    def __init__(self, ogr_ds, mode="copy", scenario=1):

        if mode == "write":
            super().__init__(ogr_ds=ogr_ds, memory=False, write=True)
        elif mode == "read":
            super().__init__(ogr_ds=ogr_ds, memory=False, write=False)
        elif mode == "empty":
            super().__init__(ogr_ds=create_empty_model().ds, memory=False)
        elif mode == "copy":
            super().__init__(ogr_ds=self.from_ds(ogr_ds), memory=False)

        logger.debug(f"Opened threedi model in {mode} mode")

        self.scenario = scenario
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326)

    def __str__(self):
        return f"3Di model, tables: {self.tables}"

    def __repr__(self):
        return f"3Di model, tables: {self.tables}"

    def __iter__(self):
        for table_name in TABLES["all"]:
            if table_name in self.layers:
                yield self.get_table(table_name)

    def from_ds(self, new_ogr_ds):
        group = create_empty_model()
        for table_name in TABLES["all"]:
            logger.info(f"Loading {table_name}")
            layer = new_ogr_ds.GetLayerByName(table_name)
            base_layer = group[table_name]
            for feature in layer:

                if table_name == "v2_connection_nodes":
                    geometry = feature.GetGeomFieldRef(1)
                else:
                    geometry = feature.geometry()

                base_layer.add(
                    items=feature.items(),
                    geometry=geometry,
                    fid=feature.GetFID(),
                )
        return group.ds

    @property
    def tables(self):
        return [l for l in TABLES["all"] + self.layers if "v2" in l]

    def get_table(self, table_name):
        """loads a table without requirements 'None'"""

        table_class = MODEL_MAPPING[table_name]

        if hasattr(table_class, "required"):
            return MODEL_MAPPING[table_name](self.ds, table_name, None)
        else:
            return MODEL_MAPPING[table_name](self.ds, table_name)

    def __getitem__(self, table):
        return self.get_table(table)

    def check_connected_table(self, table):
        if not "connected_tables" in table.properties:
            return

        table_properties = table.properties["connected_tables"]
        for connected_name, connected_fields in table_properties.items():

            connected_table = self[connected_name]
            connected_fids = connected_table.fids
            for feature in table:
                for field in connected_fields:
                    try:
                        feature[field]
                    except Exception as e:
                        print(e, field, connected_table)

                    if not feature[field] in connected_fids:
                        raise ThreediConnectedTableError(
                            """id not found""",
                            table.name,
                            connected_table.name,
                            field,
                            feature[field],
                        )

    def write_model(self, path, check=True):
        """whilst copy layer is faster than iterating over every feature,
        we want check the feature on field types and use the sqlite constraints
        therefore iteration is chosen here"""

        # check connections
        if check:
            for table in self:
                self.check_connected_table(table)

        shutil.copyfile(EMPTY_SQLITE_PATH, path)
        output = ThreediVectorGroup(ogr.Open(path, 1), mode="write")

        for table in self:
            if table.name == "v2_aggregation_settings":
                continue

            """ iterating over feature method to do checks"""
            table_output = output[table.name]
            for feature in table:
                table_output.add(feature, custom_fid=None)

        table_output = None
        output = None


def create_empty_model():
    """creates a ThreediModelBase from scratch"""
    group = VectorGroup.from_scratch(name="Threedi Model")
    for name, threedi_property in Properties():
        # create vector, with the right geometry and fields
        if "the_geom" in threedi_property:
            geometry_type = threedi_property["the_geom"]["type"]
        else:
            geometry_type = ogr.wkbUnknown

        vector = Vector.from_scratch(name, geometry_type, 4326)

        for i, (field_name, field_values) in enumerate(threedi_property.items()):
            if field_name in ["connected_tables", "the_geom", "id"]:
                continue
            vector.add_field(field_name, field_values["type"])

        # add  to the group
        group.add(vector, name)

    return group
