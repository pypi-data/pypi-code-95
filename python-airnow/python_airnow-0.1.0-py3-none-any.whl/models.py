import datetime
import inspect
import json
import sys

from dataclasses import dataclass
from dataclasses import field

from dateutil import parser

from .utils import tzinfos


class AirNowJSONDecoder(json.JSONDecoder):
    def __init__(self):
        super(AirNowJSONDecoder, self).__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if "DateObserved" in d:
                return AirNowObservation(**d)
            elif "DateForecast" in d:
                return AirNowForecast(**d)
            elif all(k in d for k in ["Number", "Name"]):
                return AirNowCategory(**d)
            else:
                return d  # pragma: no cover


@dataclass
class AirNowCategory:
    """"""

    Number: int
    Name: str


@dataclass
class AirNowObservation:
    """"""

    DateTime: datetime.datetime = field(init=False)
    DateObserved: str = field(repr=False)
    HourObserved: int = field(repr=False)
    LocalTimeZone: str = field(repr=False)
    ReportingArea: str
    StateCode: str = field(repr=False)
    Latitude: float = field(repr=False)
    Longitude: float = field(repr=False)
    ParameterName: str
    AQI: int
    Category: AirNowCategory = field(repr=False)

    def __post_init__(self):
        self.DateTime = parser.parse(
            f"\
            {self.DateObserved.strip()} \
            {self.HourObserved:01d}:00 \
            {self.LocalTimeZone}",
            tzinfos=tzinfos,
        )


@dataclass
class AirNowForecast:
    """Forecast

    Args:
        DateIssue (datetime.date): Date the forecast was issued.
        DateForecast (datetime.date): Date for which the forecast applies.
        ReportingArea (str): City or area name for which the forecast applies.
        StateCode (str): Two-character state abbreviation.
        Latitude (float): Latitude in decimal degrees.
        Longitude (float): Longitude in decimal degrees.
        ParameterName (str): Forecasted parameter name.
        AQI (int): Numerical AQI value forecasted. When a numerical AQI value is not
            available, such as when only a categorical forecast has been submitted,
            a -1 will be returned.
        Category (AirNowCategory): Forecasted category.
        ActionDay (bool): Action day status (true or false).
        Discussion (str, optional): Forecast discussion narrative. Defaults to None.
    """

    DateIssue: str = field(repr=False)
    DateForecast: str
    ReportingArea: str
    StateCode: str = field(repr=False)
    Latitude: float = field(repr=False)
    Longitude: float = field(repr=False)
    ParameterName: str
    AQI: int
    Category: AirNowCategory = field(repr=False)
    ActionDay: bool = field(repr=False)
    Discussion: str = field(repr=False, default="")

    def __post_init__(self):
        self.DateIssue = parser.parse(self.DateIssue).date()
        self.DateForecast = parser.parse(self.DateForecast).date()


@dataclass
class AirNowBBoxObservation:
    """"""

    pass
