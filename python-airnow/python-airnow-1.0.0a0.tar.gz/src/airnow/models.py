"""AirNow Models"""

import datetime
import inspect
import json
import sys

from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

import humps

from dateutil import parser
from shapely import geometry

from .utils import tzinfos


class AirNowJSONDecoder(json.JSONDecoder):
    """JSON Decoder to detect and create appropriate AirNow objects."""

    def __init__(self):
        super(AirNowJSONDecoder, self).__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        """Detect AirNow object based on keys.

        Args:
            d (dict): Dictionary of JSON data.
        """

        # Depascalize keys in dictionary for to keeps variables pythonic
        d = humps.depascalize(d)
        if "AQI" in d:
            d["aqi"] = d.pop("AQI")

        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if "date_observed" in d:
                return AirNowObservation(**d)
            elif "date_forecast" in d:
                return AirNowForecast(**d)
            elif all(k in d for k in ["number", "name"]):
                return AirNowCategory(**d)
            else:
                return d  # pragma: no cover


@dataclass
class AirNowCategory:
    """Category object

    Possible AQI category number:
        1. Good
        2. Moderate
        3. Unhealthy for Sensitive Groups
        4. Unhealthy
        5. Very Unhealthy
        6. Hazardous
        7. Unavailable

    Possible AQI category names:
        - Good
        - Moderate
        - Unhealthy for Sensitive Groups
        - Unhealthy
        - Very Unhealthy
        - Hazardous
        - Unavailable

    Args:
        number (int): AQI category number.
        name (str): AQI category name.
    """

    number: int
    name: str


@dataclass
class AirNowObservation:
    """Observation object

    Args:
        date_observed (datetime.date): Date of observation.
        hour_observed (int): Hour of observation (00-23).
        local_time_zone (str): Time zone of observed data value.
        reporting_area (str): City or area name for which the forecast applies (data
            values are peak of monitoring sites associated with this area).
        state_code (str): Two-character state abbreviation.
        latitude (float): Latitude in decimal degrees.
        longitude (float): Longitude in decimal degrees.
        parameter_name (str): Forecasted parameter name.
        aqi (int: Observed AQI category number.
        category (AirNowCategory): Observed AQI category name.
    """

    date_time: datetime.datetime = field(init=False)
    date_observed: InitVar[str]
    hour_observed: InitVar[int]
    local_time_zone: InitVar[str]

    reporting_area: str
    state_code: str = field(repr=False)

    point: geometry.Point = field(repr=False, init=False)
    latitude: InitVar[float]
    longitude: InitVar[float]

    parameter_name: str
    aqi: int
    category: AirNowCategory = field(repr=False)

    def __post_init__(
        self, date_observed, hour_observed, local_time_zone, latitude, longitude
    ):
        self.date_time = parser.parse(
            f"\
            {date_observed.strip()} \
            {hour_observed:01d}:00 \
            {local_time_zone}",
            tzinfos=tzinfos,
        )
        self.point = geometry.Point(latitude, longitude)


@dataclass
class AirNowForecast:
    """Forecast object

    Args:
        date_issue (datetime.date): Date the forecast was issued.
        date_forecast (datetime.date): Date for which the forecast applies.
        reporting_area (str): City or area name for which the forecast applies.
        state_code (str): Two-character state abbreviation.
        latitude (float): Latitude in decimal degrees.
        longitude (float): Longitude in decimal degrees.
        parameter_name (str): Forecasted parameter name.
        aqi (int): Numerical AQI value forecasted. When a numerical AQI value is not
            available, such as when only a categorical forecast has been submitted,
            a -1 will be returned.
        category (AirNowCategory): Forecasted category.
        action_day (bool): Action day status (true or false).
        discussion (str, optional): Forecast discussion narrative. Defaults to "".
    """

    date_issue: str = field(repr=False)
    date_forecast: str

    reporting_area: str
    state_code: str = field(repr=False)

    point: geometry.Point = field(repr=False, init=False)
    latitude: InitVar[float]
    longitude: InitVar[float]

    parameter_name: str
    aqi: int
    category: AirNowCategory = field(repr=False)
    action_day: bool = field(repr=False)
    discussion: str = field(repr=False, default="")

    def __post_init__(self, latitude, longitude):
        self.date_issue = parser.parse(self.date_issue).date()
        self.date_forecast = parser.parse(self.date_forecast).date()
        self.point = geometry.Point(latitude, longitude)


@dataclass
class AirNowBBoxObservation:
    """BBox Observation Object"""

    pass
