import geopy.distance
from shapely.geometry import LinearRing, shape
from . import utils
from .. import data
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px


class DistanceCalculator():
    """Class to calculate distance between county and border of germany
    """

    def __init__(self):
        """Initialize
        """
        # load geodata
        self.df_geo = utils.load_geodata()
        # this projection preserves distance better than the one we use for visualization
        self.crs = "epsg:32662"
        # create border of germany
        germany = self.df_geo.dissolve()
        buffered = germany.to_crs(self.crs).buffer(10000).to_crs(germany.crs)
        self.border = buffered.boundary.to_crs(self.crs).explode().iloc[0]
        self.border_shape = shape(self.border)
        self.pol_ext = LinearRing(self.border_shape.coords)

    def distance(self, kreis_key):
        """Calculate distance between county and border"""
        # calculate midpoint of county
        kreis_geom = self.df_geo[self.df_geo["RS"] == kreis_key]
        center_point = kreis_geom.to_crs(self.crs).centroid
        center_point.reset_index(drop=True, inplace=True)

        # Calculate nearest point on boundary
        # https://stackoverflow.com/questions/33311616/find-coordinate-of-the-closest-point-on-polygon-in-shapely/33324058#33324058
        d = self.pol_ext.project(center_point.geometry.loc[0])
        p = self.pol_ext.interpolate(d)
        cp_x, cp_y = center_point.geometry.loc[0].coords[0]
        closest = list(p.coords)[0]

        # convert to original crs
        point_geometry = gpd.points_from_xy(
            x=[cp_x, closest[0]], y=[cp_y, closest[1]])
        point_df = gpd.GeoDataFrame(
            {}, geometry=point_geometry, crs=self.crs).to_crs(self.df_geo.crs)

        # use geopy to return geodesic distance
        return geopy.distance.geodesic(point_df.loc[0, "geometry"].coords[0], point_df.loc[1, "geometry"].coords[0]).kilometers
