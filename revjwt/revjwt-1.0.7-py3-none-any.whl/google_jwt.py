from typing import Any, Dict

from google.auth.transport import requests
from google.oauth2 import id_token


def decode(token: str, client_id: str) -> Dict[str, Any]:
    request = requests.Request()

    id_info = id_token.verify_oauth2_token(token, request, client_id)

    if id_info["iss"] != "accounts.google.com":
        raise ValueError("Wrong issuer.")

    return id_info  # type: ignore
