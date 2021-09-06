# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:52:59 2021
from raster-tools
"""
from osgeo import ogr


class Layer(object):
    """
    Usage:
        >>> with Layer(geometry) as layer:
        ...     # do ogr things.
    """

    def __init__(self, geometry):
        driver = ogr.GetDriverByName(str("Memory"))
        self.data_source = driver.CreateDataSource("")
        sr = geometry.GetSpatialReference()
        self.layer = self.data_source.CreateLayer(str(""), sr)
        layer_defn = self.layer.GetLayerDefn()
        feature = ogr.Feature(layer_defn)
        feature.SetGeometry(geometry)
        self.layer.CreateFeature(feature)

    def __enter__(self):
        return self.layer

    def __exit__(self, exc_type, exc_value, traceback):
        pass
