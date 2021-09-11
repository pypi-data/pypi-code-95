import base64
import sys
from typing import Dict

import pkg_resources

from benchling_api_client.client import AuthenticatedClient


class BenchlingApiClient(AuthenticatedClient):
    def get_headers(self) -> Dict[str, str]:
        """ Get headers to be used in authenticated endpoints """
        python_version = ".".join(
            [str(x) for x in (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)]
        )
        try:
            sdk_version = pkg_resources.get_distribution("benchling-sdk").version
        except (pkg_resources.RequirementParseError, TypeError):
            sdk_version = "Unknown"
        token_encoded = base64.b64encode(f"{self.token}:".encode())
        return {
            "User-Agent": f"BenchlingSDK/{sdk_version} (Python {python_version})",
            "Authorization": f"Basic {token_encoded.decode()}",
        }
