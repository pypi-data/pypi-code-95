#
# Geo Accessor for DataFrames
#
import pandas as pd
from ._array import GeosArray
from ._delegated_dataframe import get_DataFrameExpandedProperty, get_DataFrameExpandedMethodUnary
from ._accessor_series import GeosSeriesAccessor

try:
    import geopandas as gpd
except ImportError:
    gpd = None


@pd.api.extensions.register_dataframe_accessor('geos')
class GeosDataFrameAccessor:
    """
    Access PyGEOS functionality through the "geos" dataframe accessor keyword.
    The functions defined here simply call the appropriate functions from :class:`~pgpd.GeosSeriesAccessor`
    and group the results.

    Example:
        >>> df = pd.DataFrame({
        ...     'a': list('abcde'),
        ...     'poly': pygeos.box(range(5), 0, range(10,15), 10),
        ...     'pt': pygeos.points(range(5), range(10,15))
        ... })
        >>> df = df.astype({'poly':'geos', 'pt':'geos'})
        >>> df
           a                                      poly            pt
        0  a  POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0))  POINT (0 10)
        1  b  POLYGON ((11 0, 11 10, 1 10, 1 0, 11 0))  POINT (1 11)
        2  c  POLYGON ((12 0, 12 10, 2 10, 2 0, 12 0))  POINT (2 12)
        3  d  POLYGON ((13 0, 13 10, 3 10, 3 0, 13 0))  POINT (3 13)
        4  e  POLYGON ((14 0, 14 10, 4 10, 4 0, 14 0))  POINT (4 14)
        >>> df.geos.has_z()
            poly     pt
        0  False  False
        1  False  False
        2  False  False
        3  False  False
        4  False  False
    """
    def __init__(self, obj):
        if gpd is not None and isinstance(obj, gpd.GeoDataFrame):
            geometry = obj._geometry_column_name
            obj = pd.DataFrame(obj).copy()
            obj[geometry] = GeosArray(obj[geometry].array.data)
        elif (obj.dtypes != 'geos').all():
            raise AttributeError('Must have at least one "geos" dtype column')
        self._obj = obj

    def from_geopandas(self):
        """
        Transform a :class:`geopandas.GeoDataFrame` into a regular DataFrame with a geos column.

        Returns:
            pandas.DataFrame: DataFrame where the geometry column is transformed into a geos dtype.

        Note:
            This function always returns a copy of the original data.
        """
        return self._obj.copy()

    def to_geopandas(self, geometry=None, crs=None):
        """
        Transform a pandas DataFrame with (at least) a "geos" dtype column to a :class:`geopandas.GeoDataFrame`.

        Args:
            geometry (string, optional): Name of the column to use as geometry; Default **Infer if there is only one geos column**
            crs (any, optional): CRS to use with GeoPandas, check the docs for more information; Default **None**

        Returns:
            geopandas.GeoDataFrame: The geopandas dataframe.

        Raises:
            ImportError: Geopandas is not installed.
            AttributeError: There are no geos dtype columns in the dataframe.
            TypeError: "geometry" column is not of geos dtype.
            ValueError: No "geometry" was passed, but there are multiple "geos" column so we cannot automatically infer.

        Note:
            This function always returns a copy of the original data.
        """
        if gpd is None:
            raise ImportError('Geopandas is required for this function')
        if isinstance(self._obj, gpd.GeoDataFrame):
            return self._obj.copy()

        geos_columns = self._obj.dtypes[self._obj.dtypes == 'geos'].index
        if geometry is not None and geometry not in geos_columns:
            raise TypeError(f'Column "{geometry}" should be of "geos" type')
        elif geometry is None:
            if len(geos_columns) != 1:
                raise ValueError('There are multiple columns of "geos", please specify which one to use as geometry')
            geometry = geos_columns[0]

        df = self._obj.copy()
        df[geometry] = df[geometry].astype(object)
        return gpd.GeoDataFrame(df, geometry=geometry, crs=crs)


# Set convenience properties and methods on DataFrame accessor
# They simply call the Series accessor equivalent for each geos column and group the result
for name in dir(GeosSeriesAccessor):
    if name.startswith('__'):
        continue

    item = getattr(GeosSeriesAccessor, name)
    if item is None:
        delattr(GeosSeriesAccessor, name)
    if isinstance(item, property) and hasattr(item.fget, '__DataFrameExpand__'):
        setattr(GeosDataFrameAccessor, name, get_DataFrameExpandedProperty(name, item.fget.__DataFrameExpand__))
    elif callable(item) and hasattr(item, '__DataFrameExpand__'):
        setattr(GeosDataFrameAccessor, name, get_DataFrameExpandedMethodUnary(name, item.__DataFrameExpand__))
