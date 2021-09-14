"""Models that relate to location-based services."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field

from pyportall.api.models.indicators import Moment, Month, DayOfWeek


class GeocodingOptions(BaseModel):
    """ Options to be used as fallback when the specific addresses do not have their own. """

    country: Optional[str] = Field("Spain", example="Spain", description="Country in English.")
    state: Optional[str] = Field(None, example="Comunidad de Madrid", description="State or region.")
    county: Optional[str] = Field(None, example="Madrid", description="County or province.")
    city: Optional[str] = Field(None, example="Madrid", description="City or municipality.")
    district: Optional[str] = Field(None, example="Justicia", description="District or neighborhood.")
    postal_code: Optional[str] = Field(None, example="28013", description="Postal code.")

    class Config:
        title = "Geocoding options"
        schema_extra = {
            "example": {
                "country": "Spain",
                "city": "Madrid"
            }
        }


class IsolineMode(str, Enum):
    """ Transportation mode to use when computing an isoline. """

    car = "car"
    truck = "truck"
    pedestrian = "pedestrian"


class IsolineOptions(BaseModel):
    """ Options to be used as fallback when the specific isolines do not have their own. """

    mode: Optional[IsolineMode] = Field(None, example=IsolineMode.car, description="Means of transport used to calculate the isoline border.")
    range_s: Optional[int] = Field(None, example=1000, description="Number of seconds to be taken into account to calculate the isoline border.")
    moment: Optional[Moment] = Field(None, example=Moment(dow=DayOfWeek.friday, month=Month.february, hour=20), description="Moment in time to use when estimating the isoline border.")

    class Config:
        title = "Isoline options"
        schema_extra = {
            "example": {
                "mode": IsolineMode.car,
                "range_s": 1000,
                "moment": Moment(dow=DayOfWeek.friday, month=Month.february, hour=20)
            }
        }


class IsovistOptions(BaseModel):
    """ Options to be used as fallback when the specific isovists do not have their own. """

    radius_m: Optional[int] = Field(None, example=150, description="Maximum number of meters to be taken into account to calculate the isovist border.")
    num_rays: Optional[int] = Field(None, example=-1, description="Number of angular steps that will define the resolution (-1 means 1 ray per field of view degree).")
    heading_deg: Optional[int] = Field(None, example=0, description="Northing in degrees, to set the direction the eyeballs are looking at.")
    fov_deg: Optional[int] = Field(None, example=360, description="Field of view in degrees, centered in the heading direction.")

    class Config:
        title = "Isovist options"
        schema_extra = {
            "example": {
                "radius_m": 1000
            }
        }
