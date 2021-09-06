# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:45:53 2021

@author: chris.kerklaan

TODO:
    1. Make fields an extension of a dictionary

"""
from osgeo import ogr

# ogr type mapping
OGR_TYPES = {
    bool: ogr.OFTBinary,
    int: ogr.OFTInteger,
    float: ogr.OFTReal,
    str: ogr.OFTString,
}

OGR_TYPES_INVERT = {
    ogr.OFTInteger: int,  # 0
    ogr.OFSTBoolean: bool,  # 1
    ogr.OFTReal: float,  # 2
    ogr.OFTRealList: float,  # 3
    ogr.OFTString: str,  # 4
    ogr.OFTStringList: str,
    ogr.OFTWideString: str,  # 6
    ogr.OFTBinary: bool,  # 8
    ogr.OFTDate: str,  # 9
    ogr.OFTTime: str,  # 10
    ogr.OFTDateTime: str,  # 11
    ogr.OFTInteger64: int,  # 12
    ogr.OFTInteger64List: int,  # 13
}


class Fields:
    """ogr fields has to act like a dicionary"""

    def __init__(self, layer):
        self.layer = layer

    def __getitem__(self, field_name):
        return self.type(field_name)

    def __setitem__(self, field_name, field_type):
        self.set_type(field_name, field_type)

    def __repr__(self):
        return str(self.items)

    @property
    def defn(self):
        return self.layer.GetLayerDefn()

    @property
    def names(self):
        return get_field_names(self.defn)

    @property
    def types(self):
        return get_field_types(self.defn)

    @property
    def type_names(self):
        return [ogr.GetFieldTypeName(n) for n in self.types]

    @property
    def items(self):
        return {n: [t, tn] for n, t, tn in zip(self.names, self.types, self.type_names)}

    def type(self, field_name):
        i = self.layer.FindFieldIndex(field_name, 0)
        ogr_type = self.defn.GetFieldDefn(i).GetType()
        return {"ogr": ogr_type, "type": OGR_TYPES_INVERT[ogr_type]}

    def add(self, field_name, ftype):
        if type(ftype) != int:
            ftype = OGR_TYPES[ftype]

        if field_name not in self.names:
            self.layer.CreateField(ogr.FieldDefn(field_name, ftype))

    def delete(self, field_name):
        self.layer.DeleteField(self.layer.FindFieldIndex(field_name, 0))

    def set_name(self, old_field_name, new_field_name):
        i = self.defn.GetFieldIndex(old_field_name)
        field_defn = self.layer.GetFieldDefn(i)
        field_defn.SetName(new_field_name)
        self.layer.AlterFieldDefn(i, field_defn, ogr.ALTER_NAME_FLAG)

    def set_type(self, field_name: str, field_type: type):
        """field type is change by changing the data"""
        ogr_type = OGR_TYPES[field_type]
        data = []

        for feature in self.layer:
            data.append(feature[field_name])

        self.layer.DeleteField(self.layer.FindFieldIndex(field_name, 0))

        defn = ogr.FieldDefn(field_name, ogr_type)
        self.layer.CreateField(defn)

        self.layer.ResetReading()
        for i, feature in enumerate(self.layer):
            value = data[i]
            if value:
                value = field_type(value)

            feature[field_name] = value
            self.layer.SetFeature(feature)

    def check_type(self, field_name, new_field_value):
        return self.type(field_name)["type"] == type(new_field_value)


class GeometryFields:
    def __init__(self, ogr_feature):
        self.ogr_feature = ogr_feature
        self.count = self.ogr_feature.GetGeomFieldCount()

    def __getitem__(self, key):
        return self.items[key]

    @property
    def translate(self):
        return {
            self.ogr_feature.GetGeomFieldDefnRef(i).name: i for i in range(self.count)
        }

    @property
    def names(self):
        return [self.ogr_feature.GetGeomFieldDefnRef(i).name for i in range(self.count)]

    @property
    def items(self):
        geom_items = {}
        for i in range(self.count):
            geometry = self.ogr_feature.GetGeomFieldRef(i)
            geom_items[self.ogr_feature.GetGeomFieldDefnRef(i).name] = geometry
        return geom_items


def get_field_defn(defn):
    return [defn.GetFieldDefn(i) for i in range(defn.GetFieldCount())]


def get_field_names(defn):
    """returns of list of column names for this field"""
    return [i.GetName() for i in get_field_defn(defn)]


def get_field_types(defn):
    """returns of list of column names for this field"""
    return [i.GetType() for i in get_field_defn(defn)]
