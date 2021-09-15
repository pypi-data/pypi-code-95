import geopandas as gpd
import os
import pyproj


def load_geodata():
    """Load geodata from shapefile

    Returns:
        gdp.GeoDataFrame:  GeoDataFrame containing regional data
    """
    df_geo = gpd.read_file(os.path.join(os.path.dirname(
        __file__),  "shapefiles", "VG250_KRS3", "VG250_KRS.shp"))
    df_geo.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    return df_geo
