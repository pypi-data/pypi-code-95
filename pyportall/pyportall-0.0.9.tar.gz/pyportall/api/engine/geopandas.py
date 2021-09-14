"""Module where the (Geo)Pandas helpers live."""

import json
import httpx
import pandas as pd
import geopandas as gpd
from typing import List, Optional, Union
from shapely.geometry import Polygon, mapping
from pydantic.types import UUID4

from pyportall.utils import jsonable_encoder
from pyportall.api.engine.core import APIHelper, ENDPOINT_AGGREGATED_INDICATORS, ENDPOINT_DISAGGREGATED_INDICATORS, ENDPOINT_GEOCODING, ENDPOINT_RESOLVE_ISOLINES, ENDPOINT_RESOLVE_ISOVISTS, ENDPOINT_DATAFRAMES
from pyportall.api.models.geopandas import PortallDataFrame, PortallDataFrameAPI
from pyportall.api.models.lbs import GeocodingOptions, IsolineOptions, IsovistOptions
from pyportall.api.models.indicators import Indicator, Moment


class GeocodingHelper(APIHelper):
    """Help with street addresses."""

    def resolve(self, df: pd.DataFrame, options: Optional[GeocodingOptions] = None) -> gpd.GeoDataFrame:
        """Find latitude and longitude for a number of street addresses.

        Turn a DataFrame with street addresses into a GeoDataFrame where the geometry column derives from the corresponding latitude and longitude, once those addresses have been properly geocoded.

        Args:
            df: DataFrame with at least one `street` column that includes full or partial addresses to be geocoded. Even though `street` is the only mandatory column and can contain arbitrary, partial or full addreses, geocoding typically works better if the full address is split into several fields. Therefore, other columns can help improve the accuracy of the geocoding process, namely `country`, `county`, `city`, `district` and `postal_code`.
            options: Default values for the `country`, `county`, `city`, `district` and `postal_code` columns of the DataFrame, when they are not present.

        Returns:
            A GeoDataFrame with all the geocoding columns plus the geometry column with the actual points derived from the geocoding process.
        """

        features = self.client.call_indicators(ENDPOINT_GEOCODING, {"df": df.to_dict(), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IsovistHelper(APIHelper):
    """Help with isolines."""

    def resolve(self, gdf: gpd.GeoDataFrame, options: Optional[IsovistOptions] = None) -> gpd.GeoDataFrame:
        """Find isovists (space visible from a given point in space).

        Turn a GeoDataFrame with points and other parameters the define isovists into another GeoDataFrame where the geometry column is formed by the polygons that translate to such isovist definitions.

        Args:
            gdf: GeoDataFrame with a `geometry` column with the target points and other columns to help define the isovists, Such columns are `radius_m`, `num_rays`, `heading_deg` and `fov_deg`.
            options: Default values for the `radius_m`, `num_rays`, `heading_deg` and `fov_deg` columns of the original GeoDataFrame, when they are not present.

        Returns:
            A GeoDataFrame with all the isovist definition columns plus a `destination` column with the original points. The geometry column now holds the actual polygons derived from computing the isovists.
        """

        features = self.client.call_indicators(ENDPOINT_RESOLVE_ISOVISTS, {"gdf": json.loads(gdf.to_json()), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IsolineHelper(APIHelper):
    """Help with isovists."""

    def resolve(self, gdf: gpd.GeoDataFrame, options: Optional[IsolineOptions] = None) -> gpd.GeoDataFrame:
        """Find isolines (space that can be reached in a certain amount of time from a given point in space).

        Turn a [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with points and other parameters the define isolines into another [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) where the geometry column is formed by the polygons that translate to such isoline definitions.

        Args:
            gdf: [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with a `geometry` column with the target points and other columns to help define the isolines, Such columns are `mode`, `range`, and `moment`.
            options: Default values for the `mode`, `range`, and `moment` columns of the original [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe), when they are not present.

        Returns:
            A [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with all the isoline definition columns plus a `destination` column with the original points. The geometry column now holds the actual polygons derived from computing the isolines.
        """

        features = self.client.call_indicators(ENDPOINT_RESOLVE_ISOLINES, {"gdf": json.loads(gdf.to_json()), "options": jsonable_encoder(options)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class IndicatorHelper(APIHelper):
    """Help with indicators."""

    def resolve_aggregated(self, gdf: gpd.GeoDataFrame, indicator: Optional[Indicator] = None, moment: Optional[Moment] = None) -> gpd.GeoDataFrame:
        """Find the value of an aggregated indicator for a number of target geometries in a particular moment in time.

        Given a moment in time, a number of geometries and a target indicator, find the aggregated indicator value for each of the geometries in the specified moment.

        Args:
            gdf: [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with a `geometry` column that stands for the geometries to be used on the calculations.
            indicator: The indicator to be computed.
            moment: The moment in time that will be used for the calculations.

        Returns:
            A copy of the original [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with a new column `value` with the computed values for each geometry.

        """
        features = self.client.call_indicators(ENDPOINT_AGGREGATED_INDICATORS, {"gdf": json.loads(gdf.to_json()), "indicator": jsonable_encoder(indicator), "moment": jsonable_encoder(moment)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")

    def resolve_disaggregated(self, polygon: Polygon, indicator: Indicator, moment: Moment) -> gpd.GeoDataFrame:
        """Find the disaggregated values for an indicator over a target geometry in a particular moment in time.

        Given a moment in time, one geometry and a target indicator, find the H3 cells underneath the given geometry and compute the indicator value for each of them.

        Args:
            polygon: Geometry to be used on the calculations.
            indicator: The indicator to be computed.
            moment: The moment in time that will be used for the calculations.

        Returns:
            A [GeoDataFrame](https://geopandas.org/data_structures.html#geodataframe) with one row per H3 cells and columns: `id` with the H3 cell id, `geometry` with the geometry of the H3 cells, `value` with the indicator value for the cell, and `weight`, which is useful if you want to aggregate the data from this disaggregated geodataframe yourself.

        """
        features = self.client.call_indicators(ENDPOINT_DISAGGREGATED_INDICATORS, {"polygon": mapping(polygon), "indicator": jsonable_encoder(indicator), "moment": jsonable_encoder(moment)})

        return gpd.GeoDataFrame.from_features(features=features, crs="EPSG:4326")


class PortallDataFrameHelper(APIHelper):
    """Help with Portall's GeoDataFrame wrappers."""

    def all(self) -> List[PortallDataFrame]:
        """Get all the dataframes available in Portall's database.

        Returns:
            A list of GeoDataFrame-compatible dataframes.
        """

        pdfs_api_json = self.client.get(ENDPOINT_DATAFRAMES)

        return [PortallDataFrame.from_api(PortallDataFrameAPI.parse_obj(pdf_api_json), self.client) for pdf_api_json in pdfs_api_json]

    def get(self, id: UUID4) -> Union[PortallDataFrame, None]:
        """Get just one of the dataframes available in Portall's database.

        Args:
            id: Id. of the dataframe to be retrieved.

        Returns:
            GeoDataFrame-compatible dataframe.
        """

        pdf_api_json = httpx.get(f"{ENDPOINT_DATAFRAMES}{id}/")

        return PortallDataFrame.from_api(PortallDataFrameAPI.parse_obj(pdf_api_json), self.client)
