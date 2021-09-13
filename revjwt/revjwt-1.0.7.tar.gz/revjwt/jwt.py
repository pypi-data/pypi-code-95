import json
from calendar import timegm
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from jwt.api_jwt import PyJWT
from jwt.exceptions import DecodeError, InvalidAudienceError, MissingRequiredClaimError

from revjwt.jws import decode as jws_decode
from revjwt.jws import encode as jws_encode


class JWT(PyJWT):
    def encode(
        self,
        payload: Dict[str, Any],
        key: str,
        algorithm: str = "RSA256",
        headers: Optional[Dict[str, Any]] = None,
        json_encoder: Any = None,
    ) -> str:
        # Check that we get a mapping
        if not isinstance(payload, Mapping):
            raise TypeError(
                "Expecting a mapping object, as JWT only supports "
                "JSON objects as payloads."
            )

        # Payload
        payload = payload.copy()
        for time_claim in ["exp", "iat", "nbf"]:
            # Convert datetime to a intDate value in known time-format claims
            if isinstance(payload.get(time_claim), datetime):
                payload[time_claim] = timegm(payload[time_claim].utctimetuple())

        json_payload = json.dumps(
            payload, separators=(",", ":"), cls=json_encoder
        ).encode("utf-8")

        return jws_encode(json_payload, key, algorithm, headers, json_encoder)

    def decode_complete(
        self,
        jwt: str,
        key: str = "",
        algorithms: List[str] = ["RS256"],
        options: Any = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        algorithms = ["RS256"]
        if options is None:
            options = {"verify_signature": True}
        else:
            options.setdefault("verify_signature", True)

        if options["verify_signature"] and not algorithms:
            raise DecodeError(
                'It is required that you pass in a value for the "algorithms" argument when calling decode().'
            )

        decoded = jws_decode(
            jwt,
            key="",
            algorithms=algorithms,
            options=options,
            **kwargs,
        )

        try:
            payload = json.loads(decoded["payload"])
        except ValueError as e:
            raise DecodeError("Invalid payload string: %s" % e)
        if not isinstance(payload, dict):
            raise DecodeError("Invalid payload string: must be a json object")

        if options["verify_signature"]:
            merged_options = {**self.options, **options}
            self._validate_claims(payload, merged_options, **kwargs)  # type: ignore

        decoded["payload"] = payload
        return decoded

    def _validate_aud(
        self, payload: Dict[str, Any], audience: Union[str, List[str]]
    ) -> None:
        if audience is None:
            return
        if audience is None and "aud" not in payload:
            return

        if audience is not None and "aud" not in payload:
            # Application specified an audience, but it could not be
            # verified since the token does not contain a claim.
            raise MissingRequiredClaimError("aud")  # type: ignore

        audience_claims = payload["aud"]

        if isinstance(audience_claims, str):
            audience_claims = [audience_claims]
        if not isinstance(audience_claims, list):
            raise InvalidAudienceError("Invalid claim format in token")
        if any(not isinstance(c, str) for c in audience_claims):
            raise InvalidAudienceError("Invalid claim format in token")

        if isinstance(audience, str):
            audience = [audience]

        if not any(aud in audience_claims for aud in audience):
            raise InvalidAudienceError("Invalid audience")


_jwt = JWT()  # type: ignore
encode = _jwt.encode
decode = _jwt.decode
