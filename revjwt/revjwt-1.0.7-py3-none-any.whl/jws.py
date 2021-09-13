import json
from typing import Any, Dict, List

import requests
from jwcrypto.jwk import JWK
from jwt.api_jws import PyJWS
from jwt.exceptions import DecodeError

from revjwt.algorithms import KMSAlgorithm

PUB_URL = "https://keys.revtel-api.com/certs.json"
PUB_STG_URL = "https://keys.revtel-api.com/certs-stg.json"

_keys: Dict[str, Dict[str, Any]] = {}


def fetch_key(kid: str, stage: str) -> Dict[str, Any]:
    if stage == "stg":
        url = PUB_STG_URL
    else:
        url = PUB_URL

    resp = requests.get(url).json()
    return [key for key in resp["keys"] if key["kid"] == kid][0]  # type: ignore


def get_key(kid: str, stage: str) -> Dict[str, Any]:
    try:
        return _keys[kid]
    except KeyError:
        key = fetch_key(kid, stage=stage)
        _keys[kid] = key
        return key


class JWS(PyJWS):
    def __init__(self, options: Any = None) -> None:
        super().__init__(options)  # type: ignore
        self._algorithms = {"RS256": KMSAlgorithm()}

    def decode_complete(
        self,
        jwt: str,
        key: str = "",
        algorithms: List[str] = ["RS256"],
        options: Any = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if options is None:
            options = {}
        merged_options = {**self.options, **options}
        verify_signature = merged_options["verify_signature"]

        if verify_signature and not algorithms:
            raise DecodeError(
                'It is required that you pass in a value for the "algorithms" argument when calling decode().'
            )

        payload, signing_input, header, signature = self._load(jwt)  # type: ignore

        json_payload = json.loads(payload.decode())
        kid = header["kid"]

        env = json_payload["env"]
        key = get_key(kid, stage=env)  # type: ignore

        key_json = JWK.from_json(json.dumps(key))
        key_pem = key_json.export_to_pem()

        self._verify_signature(signing_input, header, signature, key_pem, algorithms)  # type: ignore

        return {
            "payload": payload,
            "header": header,
            "signature": signature,
        }


_jws = JWS()
encode = _jws.encode
decode = _jws.decode_complete
