"""Portall's GeoDataFrame wrappers."""
from __future__ import annotations

import geopandas as gpd
from typing import Optional
from pydantic.types import UUID4
from pydantic import BaseModel, Field

from pyportall.api.engine.core import APIClient, ENDPOINT_DATAFRAMES
from pyportall.api.models.geojson import FeatureCollection, Feature, Polygon
from pyportall.exceptions import ValidationError


class PortallDataFrame(gpd.GeoDataFrame):
    """ GeoDataFrame with Portall superpowers. """

    def __init__(self, client: APIClient, name: Optional[str] = None, id: Optional[UUID4] = None, description: Optional[str] = None, *args, **kwargs) -> None:
        """Class constructor to attach the corresponding API client.

        Args:
            client: API client object to be used to send requests to the dataframe API.
            name: Dataframe name in Portall.
            id: Dataframe ID in Portall.
            description: Dataframe description in Portall.
        """
        super().__init__(*args, **kwargs)  # Needs to go first, otherwise you get a RecursionError from Pandas

        self.client = client
        self.name = name
        self.id = id
        self.description = description

    @staticmethod
    def from_gdf(gdf: gpd.GeoDataFrame, client: APIClient, name: Optional[str] = None, id: Optional[UUID4] = None, description: Optional[str] = None) -> PortallDataFrame:
        """Build from GeoDataFrame.

        Return a PortallDataFrame object out of a standard GeoPandas' GeoDataFrame.

        Args:
            gdf: GeoDataFrame to build the new PortallDataFrame object from.
            client: API client object to be used to send requests to the dataframe API.
            name: Dataframe name in Portall.
            id: Dataframe ID in Portall.
            description: Dataframe description in Portall.

        Returns:
            A new PortallDataFrame object.
        """
        pdf = PortallDataFrame(client, name=name, id=id, description=description)
        pdf.__dict__.update(gdf.__dict__)

        return pdf

    @staticmethod
    def from_geojson(geojson: FeatureCollection, client: APIClient, name: Optional[str] = None, id: Optional[UUID4] = None, description: Optional[str] = None) -> PortallDataFrame:
        """Build from GeoJSON.

        Return a PortallDataFrame object out of a standard GeoPandas' GeoDataFrame.

        Args:
            geojson: FeatureCollection GeoJSON to build the new PortallDataFrame object from.
            client: API client object to be used to send requests to the dataframe API.
            name: Dataframe name in Portall.
            id: Dataframe ID in Portall.
            description: Dataframe description in Portall.

        Returns:
            A new PortallDataFrame object.
        """
        return PortallDataFrame.from_gdf(gpd.GeoDataFrame.from_features(features=geojson.dict()["features"], crs="EPSG:4326"), client, name=name, id=id, description=description)

    @staticmethod
    def from_api(pdf_api: PortallDataFrameAPI, client: APIClient) -> PortallDataFrame:
        """Build from a Portall dataframe as returned directly by Portall's API.

        Return a PortallDataFrame object out of a Portall dataframe as returned directly by Portall's API.

        Args:
            pdf_api: PortallDataFrameAPI object to build the new PortallDataFrame object from.
            client: API client object to be used to send requests to the dataframe API.

        Returns:
            A new PortallDataFrame object.
        """
        return PortallDataFrame.from_geojson(pdf_api.geojson, client, name=pdf_api.name, id=pdf_api.id, description=pdf_api.description)

    def save(self) -> None:
        """Persist dataframe in Portall.

        Creates or updates an equivalent, remote PortallDataFrame object in Portall.
        """
        try:
            pdf_api = PortallDataFrameAPI(id=getattr(self, "id", None), name=getattr(self, "name"), description=getattr(self, "descripton", None), geojson=FeatureCollection.parse_raw(self.to_json()))
        except AttributeError:
            raise ValidationError

        if pdf_api.id is None:
            self.client.post(ENDPOINT_DATAFRAMES, body=pdf_api.json(exclude_none=True))
        else:
            self.client.put(f"{ENDPOINT_DATAFRAMES}{pdf_api.id}/", body=pdf_api.json(exclude_none=True))

    def delete(self) -> None:
        """Delete dataframe in Portall.

        Deletes remote PortallDataFrame object in Portall. It will not delete the actual Python object.
        """
        try:
            pdf_api = PortallDataFrameAPI(id=getattr(self, "id", None), name=getattr(self, "name"), description=getattr(self, "descripton", ""), geojson=self.to_json())
        except AttributeError:
            raise ValidationError

        self.client.delete(f"{ENDPOINT_DATAFRAMES}{pdf_api.id}/")
        self.id = None


class PortallDataFrameAPI(BaseModel):
    """ Representation of a Portall dataframe straight from the API. """

    id: Optional[UUID4] = Field(None, example="df30e466-1f68-42e5-8f4c-eceb1ebda89a", description="Portall ID of the saved dataframe in question.")
    name: str = Field(..., example="Population")
    description: Optional[str] = Field("", example="Population information in my trade areas.")
    geojson: FeatureCollection = Field(..., example={
        "type": "FeatureCollection",
        "features": [
            Feature(geometry=Polygon(coordinates=[[[-3.705759292, 40.428465661], [-3.705876855, 40.428428953], [-3.705893649, 40.428328537], [-3.705792879, 40.428264828], [-3.705675317, 40.428301536], [-3.705658523, 40.428401952], [-3.705759292, 40.428465661]]]), properties={"id": 631507574776148991, "value": 80.76923076915}),
            Feature(geometry=Polygon(coordinates=[[[-3.705843269, 40.428629786], [-3.705960832, 40.428593078], [-3.705977625, 40.428492662], [-3.705876855, 40.428428953], [-3.705759292, 40.428465661], [-3.705742499, 40.428566077], [-3.705843269, 40.428629786]]]), properties={"id": 631507574776151039, "value": 126.92307692295})
        ]
    })

    class Config:
        schema_extra = {
            "example": {
                "id": "df30e466-1f68-42e5-8f4c-eceb1ebda89a",
                "name": "Population",
                "description": "Population information in my trade areas.",
                "geojson": {
                    "type": "FeatureCollection",
                    "features": [
                        Feature(geometry=Polygon(coordinates=[[[-3.705759292, 40.428465661], [-3.705876855, 40.428428953], [-3.705893649, 40.428328537], [-3.705792879, 40.428264828], [-3.705675317, 40.428301536], [-3.705658523, 40.428401952], [-3.705759292, 40.428465661]]]), properties={"id": 631507574776148991, "value": 80.76923076915}),
                        Feature(geometry=Polygon(coordinates=[[[-3.705843269, 40.428629786], [-3.705960832, 40.428593078], [-3.705977625, 40.428492662], [-3.705876855, 40.428428953], [-3.705759292, 40.428465661], [-3.705742499, 40.428566077], [-3.705843269, 40.428629786]]]), properties={"id": 631507574776151039, "value": 126.92307692295})
                    ]
                }
            }
        }
