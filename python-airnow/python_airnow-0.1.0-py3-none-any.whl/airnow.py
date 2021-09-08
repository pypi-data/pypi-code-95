import datetime
import functools
import inspect
import json

import requests

from .models import AirNowBBoxObservation
from .models import AirNowForecast
from .models import AirNowJSONDecoder
from .models import AirNowObservation


class AirNow(object):
    """[summary]

    Args:
        object ([type]): [description]
    """

    def __init__(self, api_key: str, session: requests.session = None):
        self.api_key = api_key
        self._session = session if session else requests.session()

        self._base_url = "https://www.airnowapi.org/aq"

    def endpoint(endpoint):
        def decorated(func):
            @functools.wraps(func)
            def wrapped(self, *args, **kwargs):

                # inspect for parameter names, merge with kwargs
                names = inspect.getfullargspec(func)[0][1:]
                params = {**dict(zip(names, args)), **kwargs}

                # validate and sanitize parameters
                sanitized = self._sanitize_parameters(params)

                # call api endpoint and retrieve data
                return self._get_data_from_endpoint(endpoint, params=sanitized)

            return wrapped

        return decorated

    def _sanitize_parameters(self, params: dict):
        """[summary]

        Args:
            params (dict): [description]

        Raises:
            ValueError: [description]
            ValueError: [description]
            ValueError: [description]
            TypeError: [description]

        Returns:
            [type]: [description]
        """

        sanitized = {
            "format": "application/json",
            "api_key": self.api_key,
        }

        for k, v in params.items():
            if k == "zipCode":
                sanitized[k] = f"{v:05d}"

            elif k == "latitude" or k == "longitude":

                if k == "latitude":
                    if v > 90 or v < -90:
                        raise ValueError

                if k == "longitude":
                    if v > 180 or v < -180:
                        raise ValueError

                sanitized[k] = f"{v:3.6f}"

            elif k == "distance":
                if v < 0:
                    raise ValueError
                else:
                    sanitized[k] = v

            elif "date" in k:
                if k == "date":
                    if isinstance(v, datetime.datetime):
                        sanitized[k] = str(v.date())
                    else:
                        raise TypeError
            else:
                sanitized[k] = v  # pragma: no cover

        return sanitized

    def _get_data_from_endpoint(self, endpoint: str, params: dict = {}):
        """[summary]

        Args:
            endpoint (str): [description]
            params (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """
        response = self._session.get(f"{self._base_url}{endpoint}", params=params)
        response.raise_for_status()
        return json.loads(response.text, cls=AirNowJSONDecoder)

    @endpoint("/observation/zipCode/current")
    def getObservationsByZipCode(
        self,
        zipCode: int,
        distance: int = None,
    ) -> AirNowObservation:
        """Takes a Zip code and distance (optional) and returns the current air quality
        observations. If a distance is supplied, it will be used only if there is no
        explicit association between an AirNow reporting area and the supplied Zip code.
        In this case, the observations for the nearest reporting area within the
        distance will be used, if available.

        Args:
            zipCode (int): Zip code
            distance (int, optional): If no reporting area is associated with the Zip
                code, current observations from a nearby reporting area within this
                distance (in miles) will be returned, if available. Defaults to None.

        Returns:
            AirNowObservation: [description]
        """
        pass  # pragma: no cover

    @endpoint("/observation/latLong/current")
    def getObservationsByLatLong(
        self,
        latitude: float,
        longitude: float,
        distance: int = None,
    ) -> AirNowObservation:
        """Takes a latitude, longitude, and distance (optional) and returns the current
        air quality observations. If a distance is supplied, it will be used only if
        there is no explicit association between an AirNow reporting area's location and
        the supplied latitude and longitude. In this case, the observations for the
        nearest reporting area within the distance will be used, if available.

        Args:
            latitude (float): Latitude in decimal degrees.
            longitude (float): Longitude in decimal degrees.
            distance (int, optional): If no reporting area is associated with the
                latitude/longitude, look for an observation from a nearby reporting area
                within this distance (in miles). Defaults to None.

        Returns:
            AirNowObservation: [description]
        """
        pass  # pragma: no cover

    @endpoint("/observation/zipCode/historical")
    def getHistoricalObservationsByZipCode(
        self,
        zipCode: int,
        date: datetime.datetime,
        distance: int = None,
    ) -> AirNowObservation:
        """Takes a Zip code, date, and distance (optional) and returns the peak air
        quality observation for that date. If a distance is supplied, it will be used
        only if there is no explicit association between a reporting area and the
        supplied Zip Code. In this case, the observations for the nearest reporting area
        within the distance will be used, if available.

        Args:
            zipCode (int): Zip code
            date (datetime.datetime): Date of observations.
            distance (int, optional): If no reporting area is associated with the Zip
                code, current observations from a nearby reporting area within this
                distance (in miles) will be returned, if available. Defaults to None.

        Returns:
            AirNowObservation: [description]
        """
        pass  # pragma: no cover

    @endpoint("/observation/latLong/historical")
    def getHistoricalObservationsByLatLong(
        self,
        latitude: float,
        longitude: float,
        date: datetime.datetime,
        distance: int = None,
    ) -> AirNowObservation:
        """Takes a latitude, longitude, date, and distance (optional) and returns the
        peak air quality observation for that date. If a distance is supplied, it will
        be used only if there is no explicit association between an AirNow reporting
        area's location and the supplied location. In this case, the observations for
        the nearest reporting area within the distance will be used, if available.

        Args:
            latitude (float): Latitude in decimal degrees.
            longitude (float): Longitude in decimal degrees.
            date (datetime.datetime): Date of observations.
            distance (int, optional): If no reporting area is associated with the
                latitude/longitude, look for an observation from a nearby reporting
                area within this distance (in miles). Defaults to None.

        Returns:
            AirNowObservation: [description]
        """
        pass  # pragma: no cover

    @endpoint("/forecast/zipCode")
    def getForecastByZipCode(
        self,
        zipCode: int,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowForecast:
        """Takes a Zip code, date (optional), and distance (optional) and returns the
        air quality forecast. If a distance is supplied, it will be used only if there
        is no explicit association between an AirNow reporting area and the supplied
        Zip Code. In this case, the forecast for the nearest reporting area within the
        distance will be used, if available.

        https://docs.airnowapi.org/forecastsbyzip/docs

        Args:
            zipCode (int): Zip code
            date (datetime.datetime, optional): Date of forecast. If date is omitted,
                the current forecast is returned. Defaults to None.
            distance (int, optional): If no reporting area is associated with the
                specified Zip Code, return a forecast from a nearby reporting area
                within this distance (in miles). Defaults to None.

        Returns:
            AirNowForecast: [description]
        """
        pass  # pragma: no cover

    @endpoint("/forecast/latLong")
    def getForecastByLatLong(
        self,
        latitude: float,
        longitude: float,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowForecast:
        """Takes a latitude, longitude, date (optional), and distance (optional) and
        returns the air quality forecast. If a distance is supplied, it will be used
        only if there is no explicit association between an AirNow reporting area's
        location and the supplied latitude/longitude. In this case, the forecast for
        the nearest reporting area within the distance will be used, if available.

        Args:
            latitude (float): Latitude in decimal degrees.
            longitude (float): Longitude in decimal degrees.
            date (datetime.datetime, optional): Date of forecast. This argument can be
                omitted completely, in which case the current forecast is returned.
                Defaults to None.
            distance (int, optional): Return a forecast from a nearby reporting area
                within this distance (in miles). Defaults to None.

        Returns:
            AirNowForecast: [description]
        """
        pass  # pragma: no cover

    def getObservationsByBBox(
        self,
        bbox,
        parameters,
        dataType,
        startDate=None,
        endDate=None,
        monitorType=None,
        verbose: int = 0,
        includerawconcentrations: int = 0,
    ) -> AirNowBBoxObservation:
        """[summary]

        Args:
            bbox ([type]): [description]
            parameters ([type]): [description]
            dataType ([type]): [description]
            startDate ([type], optional): [description]. Defaults to None.
            endDate ([type], optional): [description]. Defaults to None.
            monitorType ([type], optional): [description]. Defaults to None.
            verbose (int, optional): [description]. Defaults to 0.
            includerawconcentrations (int, optional): [description]. Defaults to 0.
        """
        pass  # pragma: no cover
