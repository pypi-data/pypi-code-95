"""Indicator-related model classes."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, validator
from pydantic.fields import Field
from pydantic.types import conint
from typing import Optional
from datetime import datetime


class Normalization(str, Enum):
    """ Geospatial normalization, where `total` means the actual value for a given area and `density` means values are normalized by area. """

    total = "total"
    density = "density"


Hour = conint(ge=0, le=23)


class DayOfWeek(str, Enum):
    """ Day of the week. """

    sunday = "sunday"
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"

    @classmethod
    def get_number(cls, dow: DayOfWeek) -> int:
        return [cls.monday, cls.tuesday, cls.wednesday, cls.thursday, cls.friday, cls.saturday, cls.sunday].index(dow) + 1  # TODO: isoweekdays


class Month(str, Enum):
    """ Month. """

    january = "january"
    february = "february"
    march = "march"
    april = "april"
    may = "may"
    june = "june"
    july = "july"
    august = "august"
    september = "september"
    october = "october"
    november = "november"
    december = "december"

    @classmethod
    def get_number(cls, month: Month) -> int:
        return [cls.january, cls.february, cls.march, cls.april, cls.may, cls.june, cls.july, cls.august, cls.september, cls.october, cls.november, cls.december].index(month) + 1


class Moment(BaseModel):
    """ Combination of hour, day of the week, month and year to be used when computing an indicator or requesting an isoline. """

    dow: DayOfWeek = Field(..., example=DayOfWeek.friday, description="Day of the week.")
    month: Month = Field(..., example=Month.february)
    hour: Hour = Field(..., example=Hour(12))
    year: int = Field(2020, example=2020)

    class Config:
        schema_extra = {
            "example": {
                "dow": DayOfWeek.friday,
                "month": Month.february,
                "hour": Hour(12)
            }
        }

    @validator("dow", "month", pre=True)
    def lower(cls, v):
        return v.lower()

    @property
    def month_number(self) -> int:
        return Month.get_number(self.month)

    @property
    def dow_number(self) -> int:
        return DayOfWeek.get_number(self.dow)

    @property
    def equivalent_datetime(self) -> datetime:
        for day_number in range(1, 8):
            equivalent_datetime = datetime(self.year, self.month_number, day_number, self.hour, 00)
            if equivalent_datetime.weekday() == self.dow_number - 1:
                return equivalent_datetime

        raise ValueError("Couldn't find equivalent date")


class Indicator(BaseModel):
    """ Defines a measurement to be computed, typically after a location and a moment have been defined. """

    code: str = Field(..., example="pop", description="Indicator code as defined in the metadata database.")
    normalization: Optional[Normalization] = Field(Normalization.total, example=Normalization.total, description="Requested geospatial normalization.")
    aggregated: Optional[bool] = Field(True, example=True, description="True means a single value is returned for the entire geometry; false means original cells and values are preserved.")
    percent: Optional[bool] = Field(False, example=False, description="Whether the value is required to be a percentage.")

    class Config:
        schema_extra = {
            "example": {
                "code": "pop",
                "normalization": Normalization.total,
                "agreggated": True,
                "percent": False
            }
        }
