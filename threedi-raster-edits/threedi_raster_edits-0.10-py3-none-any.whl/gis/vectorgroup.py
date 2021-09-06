# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 16:45:07 2021

@author: chris.kerklaan
"""

# First-party imports
import os
import pathlib

# Third-party imports
from osgeo import ogr

# Local imports
from .vector import Vector, driver_extension_mapping


# globals
OGR_MEM_DRIVER = ogr.GetDriverByName("Memory")


class VectorGroup:
    def __init__(
        self,
        path=None,
        ogr_ds=None,
        options={},
        memory=True,
        write=False,
    ):
        """vector groups"""
        if path is not None:
            self.ext = pathlib.Path(path).suffix
            self.ds = ogr.Open(path, write, **options)

        elif ogr_ds is not None:
            self.ds = ogr_ds

        if memory:
            self.ds = self.load_to_memory(self.ds)

    @classmethod
    def from_pg(cls, host, port, user, password, dbname, write=False, memory=False):
        pg_string = ("PG:host={} port={} user='{}'" "password='{}' dbname='{}'").format(
            host, port, user, password, dbname
        )

        return cls(ogr_ds=ogr.Open(pg_string, write), memory=memory)

    @classmethod
    def from_scratch(cls, name="memdata"):
        return cls(ogr_ds=OGR_MEM_DRIVER.CreateDataSource(name), memory=False)

    def __getitem__(self, i):
        return Vector.from_ds(self.ds, layer_name=i)

    @property
    def layers(self):
        return [layer.GetName() for layer in self.ds]

    @property
    def drivers(self):
        return driver_extension_mapping()

    def add(self, vector, name):
        self.ds.CopyLayer(vector.layer, name)

    def add_styling(self, vector, name="layer_styles"):
        """add styling to the gpkg by adding the layer_styles column"""
        self.add(vector, name)

    def clear(self):
        for table in self:
            table.delete_all()

    def load_to_memory(self, ds):
        new_ds = OGR_MEM_DRIVER.CopyDataSource(ds, "")
        ds = None
        return new_ds

    def write(self, path):
        driver_name = self.drivers[os.path.splitext(path)[-1]]
        driver = ogr.GetDriverByName(driver_name)
        out_db = driver.CopyDataSource(self.ds, path)
        out_db.Destroy()

    def execute_sql(self, sql, dialect=None):
        self.ds.ExecuteSQL(sql, dialect)


def pg_string(host, port, user, password, dbname):
    return
