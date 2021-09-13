from typing import Any, Dict

import jwt

from revjwt.cert import prod_cert, stg_cert


class RevJWKClient(jwt.PyJWKClient):
    """
    monkey patch PyJWKClient, to use static keys rather than fetching
    """

    def __init__(self, data: Any) -> None:
        # explicitly pass "alg" and "use" field, so PyJWK can work normally
        _data = {
            "keys": [{"alg": "RS256", "use": "sig", **key} for key in data.get("keys")]
        }
        self._data = _data

    def fetch_data(self) -> Any:
        return self._data


def decode_static(token: str) -> Dict[str, Any]:
    """
    use static cert rather than fetched ones to perform jwt decode
    """

    decoded = jwt.decode(token, options={"verify_signature": False})
    jwk_client = RevJWKClient(stg_cert if decoded["env"] == "stg" else prod_cert)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    # TODO: verify the audience
    return jwt.decode(
        token, signing_key.key, algorithms=["RS256"], options={"verify_aud": False}
    )
