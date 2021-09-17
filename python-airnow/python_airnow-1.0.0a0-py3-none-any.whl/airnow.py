"""AirNow
"""

import datetime
import json

import humps
import requests

from .models import AirNowForecast
from .models import AirNowJSONDecoder
from .models import AirNowObservation


class AirNow(object):
    """AirNow object to retrieve air quality data via RESTful API.

    Args:
        api_key (str): API Key
        session (requests.session, optional): requests.session. Defaults to None.
    """

    def __init__(self, api_key: str, session: requests.session = None):
        self.api_key = api_key
        self._session = session if session else requests.session()

        self.observation = ObservationEndpoint(api_key, self._session)
        self.forecast = ForecastEndpoint(api_key, self._session)


class BaseEndpoint:
    """Base endpoint object to santize and retrieve data from endpoint.

    Args:
        endpoint_url (str): Endpoint to append to base url.
        api_key (str): API Key
        session (requests.session, optional): requests.session. Defaults to None.
    """

    def __init__(
        self, endpoint_url: str, api_key: str, session: requests.session = None
    ):
        self._base_url = f"https://www.airnowapi.org/aq/{endpoint_url}/"
        self.api_key = api_key
        self._session = session if session else requests.session()

    def get_data_from_endpoint(self, endpoint: str, params: dict):
        """Sanitize API parameters and retrieve data from airnow.org API

        Args:
            endpoint (str): Endpoint.
            params (dict): Parameters.
        """
        sanitized = self._sanitize_parameters(params)
        return self._get_data_from_endpoint(endpoint, params=sanitized)

    def _sanitize_parameters(self, params: dict):
        """Sanitize parameters for API consumption.

        Args:
            params (dict): AirNow API parameters.
        """
        sanitized = {
            "api_key": self.api_key,
        }

        sanitized["format"] = (
            "application/json" if "format" not in params else params.get("format")
        )

        for k, v in humps.camelize(params).items():

            if v is None or k == "self":
                continue

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

                    elif isinstance(v, str):
                        sanitized[k] = v

                    else:
                        raise TypeError

            else:
                sanitized[k] = v  # pragma: no cover

        return sanitized

    def _get_data_from_endpoint(self, endpoint: str, params: dict = {}):
        """Fetch data from airnow.org API

        Args:
            endpoint (str): Endpoint.
            params (dict): Parameters.
        """
        response = self._session.get(f"{self._base_url}{endpoint}", params=params)
        response.raise_for_status()
        return json.loads(response.text, cls=AirNowJSONDecoder)


class ObservationEndpoint(BaseEndpoint):
    """Observation endpoint object to get data for current or historical observations.

    Args:
        api_key (str): API Key
        session (requests.session, optional): requests.session. Defaults to None.
    """

    def __init__(self, api_key: str, session: requests.session = None):
        super(ObservationEndpoint, self).__init__("observation", api_key, session)

    def by_zip_code(
        self,
        zip_code: int,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowObservation:
        """Get current/historical AQI for a reporting area by Zip code.

        Takes a Zip code and distance (optional) and returns the current air quality
        observations. If a distance is supplied, it will be used only if there is no
        explicit association between an AirNow reporting area and the supplied Zip code.
        In this case, the observations for the nearest reporting area within the
        distance will be used, if available.

        Args:
            zip_code (int): Zip code
            date (datetime.datetime, optional): Date of observations. Defaults to None.
            distance (int, optional): If no reporting area is associated with the Zip
                code, current observations from a nearby reporting area within this
                distance (in miles) will be returned, if available. Defaults to None.

        Returns:
            AirNowObservation: [description]
        """

        if date is not None:
            date = f"{date.date()}T00-0000"
            return self.get_data_from_endpoint("zipCode/historical", locals())
        else:
            return self.get_data_from_endpoint("zipCode/current", locals())

    def by_lat_long(
        self,
        latitude: float,
        longitude: float,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowObservation:
        """Get current AQI for a reporting area by latitude and longitude.

        Takes a latitude, longitude, and distance (optional) and returns the current
        air quality observations. If a distance is supplied, it will be used only if
        there is no explicit association between an AirNow reporting area's location and
        the supplied latitude and longitude. In this case, the observations for the
        nearest reporting area within the distance will be used, if available.

        Args:
            latitude (float): Latitude in decimal degrees.
            longitude (float): Longitude in decimal degrees.
            date (datetime.datetime, optional): Date of observations. Defaults to None.
            distance (int, optional): If no reporting area is associated with the
                latitude/longitude, look for an observation from a nearby reporting area
                within this distance (in miles). Defaults to None.

        Returns:
            AirNowObservation: [description]
        """
        if date is not None:
            date = f"{date.date()}T00-0000"
            return self.get_data_from_endpoint("latLong/historical", locals())
        else:
            return self.get_data_from_endpoint("latLong/current", locals())


class ForecastEndpoint(BaseEndpoint):
    """Forecast endpoint object to get data for forecasts.

    Args:
        api_key (str): API Key
        session (requests.session, optional): requests.session. Defaults to None.
    """

    def __init__(self, api_key: str, session: requests.session = None):
        super(ForecastEndpoint, self).__init__("forecast", api_key, session)

    def by_zip_code(
        self,
        zip_code: int,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowForecast:
        """Get current or historical forecasted AQI for a reporting area by Zip code.

        Takes a Zip code, date (optional), and distance (optional) and returns the
        air quality forecast. If a distance is supplied, it will be used only if there
        is no explicit association between an AirNow reporting area and the supplied
        Zip Code. In this case, the forecast for the nearest reporting area within the
        distance will be used, if available.

        https://docs.airnowapi.org/forecastsbyzip/docs

        Args:
            zip_code (int): Zip code
            date (datetime.datetime, optional): Date of forecast. If date is omitted,
                the current forecast is returned. Defaults to None.
            distance (int, optional): If no reporting area is associated with the
                specified Zip Code, return a forecast from a nearby reporting area
                within this distance (in miles). Defaults to None.

        Returns:
            AirNowForecast: [description]
        """
        return self.get_data_from_endpoint("zipCode", locals())

    def by_lat_long(
        self,
        latitude: float,
        longitude: float,
        date: datetime.datetime = None,
        distance: int = None,
    ) -> AirNowForecast:
        """Get current or historical forecasted AQI for a reporting area by latitude
        and longitude.

        Takes a latitude, longitude, date (optional), and distance (optional) and
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
        return self.get_data_from_endpoint("latLong", locals())
