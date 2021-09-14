"""Module where core API-related classes live."""

import os
import httpx
import json
from typing import Any, Dict, Optional
from time import sleep

from pyportall.exceptions import AuthError, BatchError, PreFlightException, PyPortallException, RateLimitError, TimeoutError, ValidationError
from pyportall.api.models.preflight import Preflight
from pyportall.utils import jsonable_encoder


BATCH_DELAY_S = 5

ENDPOINT_METADATA = os.getenv("PYPORTALL_ENDPOINT_METADATA", "https://portall-api.inspide.com/v0/metadata/indicators/")
ENDPOINT_DATAFRAMES = os.getenv("PYPORTALL_ENDPOINT_DATAFRAMES", "https://portall-api.inspide.com/v0/data/dataframes/")
ENDPOINT_GEOCODING = os.getenv("PYPORTALL_ENDPOINT_GEOCODING", "https://portall-api.inspide.com/v0/pyportall/geocoding.geojson")
ENDPOINT_RESOLVE_ISOVISTS = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOVISTS", "https://portall-api.inspide.com/v0/pyportall/isovists.geojson")
ENDPOINT_RESOLVE_ISOLINES = os.getenv("PYPORTALL_ENDPOINT_RESOLVE_ISOLINES", "https://portall-api.inspide.com/v0/pyportall/isolines.geojson")
ENDPOINT_AGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_AGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicators.geojson")
ENDPOINT_DISAGGREGATED_INDICATORS = os.getenv("PYPORTALL_ENDPOINT_DISAGGREGATED_INDICATORS", "https://portall-api.inspide.com/v0/pyportall/indicator.geojson")


class APIClient:
    """This class holds the direct interface to Portall's API. Other classes may need to use one API client to actually send requests to the API."""

    def __init__(self, api_key: Optional[str] = None, batch: Optional[bool] = False, preflight: Optional[bool] = False) -> None:
        """When instantiating an API client, you will provide an API key and optionally opt for batch or preflight modes.

        In preflight mode, requests to the API will not be executed. Instead, the API returns the estimated cost in credits for such request.

        Use batch mode when requests take longer to execute than the default API timeout (around 15s).

        Args:
            api_key: API key to use with Portall's API, in case no API key is available via the `PYPORTALL_API_KEY` environment variable. Please contact us if you need one.
            batch: Whether the client will work in batch mode or not.
            preflight: Whether the client will work in preflight mode or not.

        Raises:
            PyPortallException: Raised if no API key is available either through the `api_key` parameter or the `PYPORTALL_API_KEY` environment variable.
        """
        self.api_key = api_key or os.getenv("PYPORTALL_API_KEY")
        if self.api_key is None:
            raise PyPortallException("API key is required to use Portall's API")
        self.batch = batch
        self.preflight = preflight

        self.last_status_code = None

    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """Send GET requests to Portall's API.

        Args:
            endpoint: URL to send the request to.
            params: Parameters to be sent as part of the final URL.
            headers: Headers to be added to the request, if any.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: Request has timed out.
        """
        params = params or {}
        params["apikey"] = self.api_key

        headers = headers or {}

        try:
            response = httpx.get(endpoint, params=params, headers=headers)
        except httpx.ReadTimeout:
            raise TimeoutError("API is timing out. If this endpoint supports batch-enabled requests, you should probably try that.")

        self.last_status_code = response.status_code
        if self.last_status_code in (200, 202):
            return response.json()
        elif self.last_status_code == 401:
            raise AuthError("Wrong API key")
        elif self.last_status_code == 429:
            raise RateLimitError(response.json()["detail"])
        else:
            raise PyPortallException(response.json())

    def post(self, endpoint: str, body: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """Send POST requests to Portall's API.

        Args:
            endpoint: URL to send the request to.
            body: JSON string.
            params: Parameters to be sent as part of the final URL.
            headers: Headers to be added to the request, apart from content-type.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: Request has timed out.
            ValidationError: The format of the request is not valid.
        """
        params = params or {}
        params["apikey"] = self.api_key

        headers = headers or {}
        headers["content-type"] = "application/json"

        try:
            response = httpx.post(endpoint, params=params, headers=headers, content=body.encode("utf8"))
        except httpx.ReadTimeout:
            raise TimeoutError("API is timing out. If this endpoint supports batch-enabled requests, you should probably try that.")

        self.last_status_code = response.status_code
        if self.last_status_code in (200, 201, 202):
            return response.json()
        elif self.last_status_code == 401:
            raise AuthError("Wrong API key")
        elif self.last_status_code == 422:
            raise ValidationError(response.json()["detail"])
        elif self.last_status_code == 429:
            raise RateLimitError(response.json()["detail"])
        else:
            raise PyPortallException(response.text)

    def put(self, endpoint: str, body: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """Send PUT requests to Portall's API.

        Args:
            endpoint: URL to send the request to.
            body: JSON string.
            params: Parameters to be sent as part of the final URL.
            headers: Headers to be added to the request, apart from content-type.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: Request has timed out.
            ValidationError: The format of the request is not valid.
        """
        params = params or {}
        params["apikey"] = self.api_key

        headers = headers or {}
        headers["content-type"] = "application/json"

        try:
            response = httpx.put(endpoint, params=params, headers=headers, content=body.encode("utf8"))
        except httpx.ReadTimeout:
            raise TimeoutError("API is timing out. If this endpoint supports batch-enabled requests, you should probably try that.")

        self.last_status_code = response.status_code
        if self.last_status_code in (200, 201, 202):
            return response.json()
        elif self.last_status_code == 401:
            raise AuthError("Wrong API key")
        elif self.last_status_code == 422:
            raise ValidationError(response.json()["detail"])
        elif self.last_status_code == 429:
            raise RateLimitError(response.json()["detail"])
        else:
            raise PyPortallException(response.text)

    def delete(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> None:
        """Send DELETE requests to Portall's API.

        Args:
            endpoint: URL to send the request to.
            params: Parameters to be sent as part of the final URL.
            headers: Headers to be added to the request, if any.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: Request has timed out.
        """
        params = params or {}
        params["apikey"] = self.api_key

        headers = headers or {}

        try:
            response = httpx.delete(endpoint, params=params, headers=headers)
        except httpx.ReadTimeout:
            raise TimeoutError("API is timing out. This is not a common thing for delete operations, so there is probably something else going on.")

        self.last_status_code = response.status_code
        if self.last_status_code == 204:
            return
        elif self.last_status_code == 401:
            raise AuthError("Wrong API key")
        elif self.last_status_code == 429:
            raise RateLimitError(response.json()["detail"])
        else:
            raise PyPortallException(response.text)

    def call_indicators(self, url: str, input: Any) -> Any:
        """Send requests to Portall's indicator API.

        Takes an arbitrary object and, as long as it can be transformed into a JSON string, sends it to the indicator API. It deals with preflight and batch mode according to the settings defined upon creation of the client.

        Args:
            url: URL of the specific API endpoint in question.
            input: Any python object that can be encoded to a JSON string.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            AuthError: Authentication has failed, probably because of a wrong API key.
            BatchError: A batch request has failed, because of an error or because the batch timeout has expired.
            PreFlightException: Raised in preflight mode, includes the number of estimated credits that the actual request would consume.
            PyPortallException: Generic API exception.
            RateLimitError: The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded.
            TimeoutError: A regular (non-batch) request has timed out.
            ValidationError: The format of the request is not valid.
        """

        query_params: Dict[str, Any] = {}
        if self.preflight is True:
            query_params["preflight"] = True
        if self.batch is True:
            query_params["batch"] = True

        response_json = self.post(url, params=query_params, body=json.dumps(jsonable_encoder(input)))

        if self.last_status_code == 200:
            if self.preflight:
                raise PreFlightException(Preflight(**response_json).detail)
            return response_json
        elif self.last_status_code == 202:
            job_url = response_json["detail"]

            while True:
                response_json = self.get(job_url)

                if self.last_status_code == 200:
                    return response_json
                elif self.last_status_code == 202:
                    sleep(BATCH_DELAY_S)
                else:
                    raise BatchError("Batch job is not available, probably because of an error or because the batch timeout has expired")
        else:
            raise PyPortallException(self.last_status_code)

    def call_metadata(self) -> Any:
        """Send requests to Portall's metadata API.

        Returns:
            The Python object derived from the JSON received by the API.

        Raises:
            PyPortallException: Generic API exception.
        """

        return self.get(ENDPOINT_METADATA)


class APIHelper:
    """Ensure a common structure for helpers that actually do things."""

    def __init__(self, client: APIClient) -> None:
        """Class constructor to attach the coresponding API client.

        Args:
            client: API client object that the helper will use to actually send requests to the API when it has to.
        """
        self.client = client
