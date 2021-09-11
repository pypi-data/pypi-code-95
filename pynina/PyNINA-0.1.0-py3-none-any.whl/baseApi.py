from typing import Any, Dict

from aiohttp import BasicAuth, ClientSession, ClientConnectionError


class BaseAPI:
    """Class to perform CMI API requests"""

    @staticmethod
    async def _makeRequest(url: str):
        """Retrieve data from API."""
        try:
            async with ClientSession() as session:
                async with session.get(url) as res:
                    if res.status != 200:
                        raise ApiError(f"Invalid response: {res.status}")

                    json: Dict[str, Any] = await res.json()
                    return json
        except ClientConnectionError:
            raise ApiError(f"Could not connect to Api")


class ApiError(Exception):
    """Raised when API request ended in error."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status