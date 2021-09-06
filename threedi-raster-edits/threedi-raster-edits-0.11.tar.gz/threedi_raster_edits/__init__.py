try:
    from osgeo import ogr

    ogr  # Pyflakes
except ImportError:
    raise (
        """ ERROR: Could not find the GDAL/OGR Python library bindings.
               On anaconda, use conda install gdal >= 3.2.0
               otherwise look at https://pypi.org/project/GDAL/"""
    )

# gis
from .gis.raster import Raster
from .gis.rastergroup import RasterGroup
from .gis.vector import Vector
from .gis.vectorgroup import VectorGroup
from .gis.linestring import LineString, MultiLineString
from .gis.polygon import Polygon, MultiPolygon
from .gis.point import Point, MultiPoint

# Threedi
from .threedi.rastergroup import ThreediRasterGroup
from .threedi.rastergroup import retrieve_soil_conversion_table
from .threedi.rastergroup import retrieve_landuse_conversion_table
from .threedi.edits import ThreediEdits

# Threedi - API
from .threedi.api.run import Simulation
from .threedi.api.run import Batch

# Lizard
from .lizard.rextract import RasterExtraction
from .lizard import uuid as UUID

# Logging
from .utils.logging import show_console_logging


# Pyflakes
Raster
RasterGroup
VectorGroup
Vector
LineString
MultiLineString
Polygon
MultiPolygon
Point
MultiPoint
ThreediRasterGroup
retrieve_soil_conversion_table
retrieve_landuse_conversion_table
RasterExtraction
UUID
ThreediEdits
Simulation
Batch
show_console_logging


__version__ = "x.x.x"

__doc__ = """
General toolbox for editing threedi models in python
"""
