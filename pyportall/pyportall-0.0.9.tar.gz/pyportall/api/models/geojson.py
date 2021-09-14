# Adapted from https://github.com/developmentseed/geojson-pydantic
import abc
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from typing import Tuple, Union
from typing import Any, Dict, List, Optional, Tuple, Union


LONG_LOG_ITEM_MAX_WIDTH = 200

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Any  # will be constrained in child classes

    @property
    def __geo_interface__(self):
        return self.dict()

    def __repr_str__(self, join_str: str) -> str:
        return join_str.join(repr(v)[:LONG_LOG_ITEM_MAX_WIDTH] if a is None else f'{a}={repr(v)[:LONG_LOG_ITEM_MAX_WIDTH]}' for a, v in self.__repr_args__())


Coordinate = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]

Position = Coordinate


class Point(_GeometryBase):
    """Point Model"""

    type: str = Field("Point", const=True)
    coordinates: Coordinate


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: str = Field("MultiPoint", const=True)
    coordinates: List[Coordinate]


class LineString(_GeometryBase):
    """LineString Model"""

    type: str = Field("LineString", const=True)
    coordinates: List[Coordinate] = Field(..., min_items=2)


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Coordinate]]


class Polygon(_GeometryBase):
    """Polygon Model"""

    type: str = Field("Polygon", const=True)
    coordinates: List[List[Coordinate]]

    @validator("coordinates")
    def check_coordinates(cls, coords):
        """Validate that Polygon coordinates pass the GeoJSON spec"""
        if any([len(c) < 4 for c in coords]):
            raise ValueError("All linear rings must have four or more coordinates")
        if any([c[-1] != c[0] for c in coords]):
            raise ValueError("All linear rings have the same start and end coordinates")
        return coords


class MultiPolygon(_GeometryBase):
    """MultiPolygon Model"""

    type: str = Field("MultiPolygon", const=True)
    coordinates: List[List[List[Coordinate]]]


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


class GeometryCollection(BaseModel):
    """GeometryCollection Model"""

    type: str = Field("GeometryCollection", const=True)
    geometries: List[Geometry]

    def __iter__(self):
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self):
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index):
        """get geometry at a given index"""
        return self.geometries[index]


def parse_geometry_obj(obj) -> Geometry:
    """
    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic Geometry model.
    """
    if "type" not in obj:
        raise ValidationError(
            [
                ErrorWrapper(ValueError("Missing 'type' field in geometry"), "type"),
                "Geometry",
            ]
        )
    if obj["type"] == "Point":
        return Point.parse_obj(obj)
    elif obj["type"] == "MultiPoint":
        return MultiPoint.parse_obj(obj)
    elif obj["type"] == "LineString":
        return LineString.parse_obj(obj)
    elif obj["type"] == "MultiLineString":
        return MultiLineString.parse_obj(obj)
    elif obj["type"] == "Polygon":
        return Polygon.parse_obj(obj)
    elif obj["type"] == "MultiPolygon":
        return MultiPolygon.parse_obj(obj)
    raise ValidationError(
        [ErrorWrapper(ValueError("Unknown type"), "type")], "Geometry"
    )


def parse_polygon_obj(obj) -> Polygon:
    """
    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic Geometry model.
    """
    if "type" not in obj:
        raise ValidationError(
            [
                ErrorWrapper(ValueError("Missing 'type' field in geometry"), "type"),
                "Geometry",
            ]
        )
    if obj["type"] == "Polygon":
        return Polygon.parse_obj(obj)
    raise ValidationError(
        [ErrorWrapper(ValueError("Unknown type"), "type")], "Polygon"
    )


class Feature(BaseModel):
    """ GeoJSON feature. """

    type: str = Field("Feature", const=True)
    geometry: Geometry
    properties: Optional[Dict[Any, Any]]
    id: Optional[str]
    bbox: Optional[BBox]

    class Config:
        schema_extra = {
            "example": {
                "type": "Feature",
                "geometry": Polygon(coordinates=[[[-3.705759292, 40.428465661], [-3.705876855, 40.428428953], [-3.705893649, 40.428328537], [-3.705792879, 40.428264828], [-3.705675317, 40.428301536], [-3.705658523, 40.428401952], [-3.705759292, 40.428465661]]]),
                "properties": {"id": 631507574776148991, "value": 80.76923076915, "weight": 1}
            }
        }
        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v):
        """set geometry from geo interface or input"""
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v


class FeatureCollection(BaseModel):
    """ GeoJSON feature collection. """

    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]
    bbox: Optional[BBox]

    class Config:
        schema_extra = {
            "example": {
                "type": "FeatureCollection",
                "features": [
                    Feature(geometry=Polygon(coordinates=[[[-3.705759292, 40.428465661], [-3.705876855, 40.428428953], [-3.705893649, 40.428328537], [-3.705792879, 40.428264828], [-3.705675317, 40.428301536], [-3.705658523, 40.428401952], [-3.705759292, 40.428465661]]]), properties={"id": 631507574776148991, "value": 80.76923076915, "weight": 1}),
                    Feature(geometry=Polygon(coordinates=[[[-3.705843269, 40.428629786], [-3.705960832, 40.428593078], [-3.705977625, 40.428492662], [-3.705876855, 40.428428953], [-3.705759292, 40.428465661], [-3.705742499, 40.428566077], [-3.705843269, 40.428629786]]]), properties={"id": 631507574776151039, "value": 126.92307692295, "weight": 1})
                ]
            }
        }

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]


GeoJSON = Union[Feature, FeatureCollection]
