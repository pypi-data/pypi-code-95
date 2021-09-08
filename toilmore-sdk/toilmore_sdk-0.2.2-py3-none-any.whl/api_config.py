"""API config."""
from typing import (
    NamedTuple,
)

from . import constants


class ApiEndpoint(NamedTuple):
    """
     A definition for the API endpoint. We use an object with a few
     fields so that we can connect to mock ups of the server during SDK testing,
     or use the SDK to play with a local copy of the running API services.
    """
    protocol: str
    host: str
    version: str
    api_module: str
    port: int

    @property
    def url_prefix(self):
        return '/imgopt3/{version}/{api_module}/'.format(
            version=self.version,
            api_module=self.api_module
        )


class ApiConfig(NamedTuple):
    """
    A simple object specifying a domain, token and endpoint to connect to.
    """
    domain: str
    api_token: str
    api_endpoint: ApiEndpoint
    debug_mode: bool = True


LIGHT_API = ApiEndpoint(
    protocol="https",
    host="accelerator.shimmercat.com",
    version="2020.1",
    api_module=constants.LIGHT_API_KEY,
    port=443,
)


LUX_API = ApiEndpoint(
    protocol="https",
    host="accelerator.shimmercat.com",
    version="2020.4",
    api_module=constants.LUX_API_KEY,
    port=443,
)


CANARY_LIGHT_API = ApiEndpoint(
    protocol="https",
    host="canary.shimmercat.com",
    version="2020.1",
    api_module=constants.LIGHT_API_KEY,
    port=443,
)


CANARY_LUX_API = ApiEndpoint(
    protocol="https",
    host="canary.shimmercat.com",
    version="2020.4",
    api_module=constants.LUX_API_KEY,
    port=443,
)
