# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 13:05:21 2021

@author: chris.kerklaan

Note:
    Spatial references can be either projected, geographic or local
    
BUG:
    cannot set the spatial reference somehow
"""

import logging
from osgeo import osr

# Logger
logger = logging.getLogger(__name__)


class SpatialReference(osr.SpatialReference):
    def __init__(self, wkt=None, centroid=None):

        if not wkt:
            if centroid:
                epsg = centroid_to_epsg(centroid)
                logger.debug(f"No spatial reference assigned, assigning epsg {epsg}")
                wkt = self.epsg_to_wkt(epsg)
            else:
                logger.debug("No spatial reference assigned, pleas asign epsg")

        if type(wkt) == int:
            logger.debug("please use SpatialReference.from_epsg")
        elif type(wkt) == osr.SpatialReference:
            logger.debug("please use SpatialReference.from_sr")

        super().__init__(wkt=wkt)

    @classmethod
    def from_epsg(cls, epsg, **kwargs):
        return cls(SpatialReference.epsg_to_wkt(epsg), **kwargs)

    @classmethod
    def from_sr(cls, sr, centroid=None):
        if sr == None:
            return cls(None, centroid)
        else:
            return cls(sr.ExportToWkt())

    @staticmethod
    def epsg_to_wkt(epsg):
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(epsg)
        return sr.ExportToWkt()

    def __getitem__(self, item):
        return self.GetAttrValue(item)

    def __str__(self):
        return self.ExportToPrettyWkt()

    @property
    def wkt(self):
        return self.ExportToWkt()

    @property
    def unit(self):
        return self["UNIT"]

    @property
    def type(self):
        if self.IsProjected:
            return "PROJCS"
        elif self.IsGeographic:
            return "GEOGCS"
        elif self.IsLocal:
            return "LOCAL"
        else:
            return None

    @property
    def original(self):
        return osr.SpatialReference(self.wkt)

    @property
    def epsg(self):
        if self.GetAuthorityName(self.type) == "EPSG":
            return int(self.GetAuthorityCode(self.type))
        else:
            self.AutoIdentifyEPSG()
            return int(self.GetAttrValue("AUTHORITY", 1))

    def transform(self, epsg=28992):
        """returns a transform between current projection and out_epsg"""
        new = SpatialReference.from_epsg(epsg)
        return osr.CoordinateTransformation(self.original, new.original)


def centroid_to_epsg(centroid):
    """estimating based on centroid coordinatess"""
    x, y = centroid.points[0]

    if -90 > x > 90 and -180 > y > 180:
        return 4326

    return 28992
