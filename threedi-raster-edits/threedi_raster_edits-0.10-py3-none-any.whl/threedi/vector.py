# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:57:13 2021

@author: chris.kerklaan
"""
# Third-party imports
import numpy as np
from osgeo import ogr


# Local imports
from threedi_raster_edits.gis.vector import Vector
from threedi_raster_edits.threedi.tables.constants import Properties
from threedi_raster_edits.threedi.tables.templates import ThreediTemplateTable
from threedi_raster_edits.threedi.feature import ThreediFeature


# Globals
PROPERTIES = Properties()


class ThreediVector(Vector):
    def __init__(self, ogr_ds, table_name):
        Vector.__init__(self, path=ogr_ds, ds=True, layer_name=table_name)
        self.edits = []
        self.name = table_name
        self.properties = PROPERTIES[table_name]

        if not hasattr(self, "layer"):
            print(table_name, "not present")
            return

    def __iter__(self):
        fids = [i.GetFID() for i in self.layer]
        for fid in fids:
            yield self.get_feature(fid)

    def __getitem__(self, i):
        return self.get_feature(i)

    def __len__(self):
        return self.count

    def __repr__(self):
        return f"3Di table {self.name}, row ids: {self.fids}"

    def __setitem__(self, key, value):
        self.layer.SetFeature(value.ptr)

    def get_feature(self, i):
        """helper for retrieving features"""
        return ThreediFeature(
            self.layer.GetFeature(i),
            self.layer,
            self.layer_name,
            properties=self.properties,
            custom_set_function=self.custom_set_function,
            set_feature=True,
        )

    def add_template(self, template: dict):
        """input is a ThreediTemplate, output is geometry, fid, attributes
        None if not present
        """
        # dervive id from template
        fid = template.get("id")
        if fid == "None":
            fid = None
        else:
            fid = int(fid)

        # derive geometry from template
        geometry = template.get("the_geom")

        # derive content from template
        attributes = {}
        for key in template.keys():
            if key in ["id", "the_geom", "table"]:
                continue
            value = template[key]
            try:
                content = value.content
            except AttributeError:
                content = value
            attributes[key] = content

        return fid, attributes, geometry

    def add(self, row, set_feature=False, custom_fid=-1):
        """Add geometry and attributes as new feature due to type checking"""
        # input can either be a feature or a template

        if type(row) == ThreediTemplateTable:
            fid, items, geometry = self.add_template(row)
        else:
            fid, items, geometry = row.fid, row.items, row.geometry

        use_custom_add = hasattr(self, "custom_add_function")
        if use_custom_add:
            fid, items, geometry = self.custom_add_function(fid, items, geometry)

        if custom_fid is not None:
            fid = custom_fid

        # add everything via threedi-feature to follow normal set procedures
        feature = ThreediFeature(
            ogr.Feature(self.layer_defn),
            self.layer,
            self.name,
            self.properties,
            set_feature,
            self.custom_set_function,
        )

        feature_count = self.layer.GetFeatureCount()

        # threedi must start from 1, is set to feature count
        if fid == None or fid == -1:
            if feature_count == 0:
                fid = 1
            else:
                fid = feature_count + 1
                while self.layer.GetFeature(fid) != None:
                    fid += 1

        for key, value in items.items():
            feature[str(key)] = value

        if geometry is not None:
            feature["the_geom"] = geometry

        if fid == 0:
            raise ValueError("Feature id cannot be 0 in 3Di")

        try:
            ogr_feature = feature.ptr
            ogr_feature.SetFID(fid)
            self.layer.CreateFeature(ogr_feature)
        except RuntimeError as e:
            raise (f"error: {e} geometry {geometry} items {feature.items}")

        # set the index
        fid = ogr_feature.GetFID()
        if geometry:
            ogr_geometry = ogr_feature.geometry()
            if ogr_geometry == None:
                ogr_geometry = ogr_feature.GetGeomFieldRef(1)

            self.set_index()
            self.idx.insert(fid, ogr_geometry.GetEnvelope())

        feature = None
        return self.layer, fid

    # @property
    # def check(self):
    #     for feature in self:
    #         for field_name, constraint in self.constraints.items():
    #             value = feature[field_name]

    #             if value and type(value) in [int, float]:
    #                 comparison, compare_field = constraint["comparison"]
    #                 if not (comparison(value, feature[compare_field])):
    #                     print(
    #                         f""" {_ANGRY}
    #                     Comparison {value} {OPS[comparison]}
    #                     {feature[compare_field]} not True """
    #                     )


class ThreediDemVector(ThreediVector):
    required = {"dem": None}

    def __init__(self, path, layer_name, dem):
        ThreediVector.__init__(self, path, layer_name)
        self.dem = dem

    def sample(self, addition=0):
        for feature in self:
            value = np.nanmean(self.dem.read(feature.geometry))
            feature["crest_level"] = value + addition
            self.set_feature(feature)
