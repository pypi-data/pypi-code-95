import random
from datetime import datetime, timedelta
from typing import Any, Dict, Sequence, Type
from uuid import uuid4

import requests

from revjwt.jwt import encode
from revjwt.utils import CERT_URL, STG_CERT_URL


class PayloadDesc:
    pass


class TypDesc(PayloadDesc):
    def __init__(self, typ: str) -> None:
        self._typ = typ

    def __get__(self, instance: Any, cls: Any) -> str:
        return self._typ


class AudDesc(PayloadDesc):
    def __get__(self, instance: Any, cls: Any) -> Any:
        return instance.client.client_id


class IatDesc(PayloadDesc):
    def __get__(self, instance: Any, cls: Any) -> int:
        now = datetime.utcnow()
        return int(now.timestamp())


class JtiDesc(PayloadDesc):
    def __get__(self, instance: Any, cls: Any) -> str:
        return uuid4().__str__()


class SubDesc(PayloadDesc):
    def __get__(self, instance: Any, cls: Any) -> Any:
        return instance.data["id"]


class GrpDesc(PayloadDesc):
    def __get__(self, instance: Any, cls: Any) -> str:
        groups = instance.data.get("groups", [])
        return ":".join(groups)


class ExpDesc(PayloadDesc):
    exp_field: str = "default_access_exp"
    duration_unit: str = "minutes"
    default_exp: int = 120

    def __init__(self, exp_field: str, dur_unit: str, default_exp: int) -> None:
        self._exp_field = exp_field
        self._dur_unit = dur_unit
        self._default_exp = default_exp

    def __get__(self, instance: Any, cls: Any) -> int:
        exp = instance.client.get(self._exp_field, self._default_exp)
        now = datetime.utcnow()
        kwargs = {self._dur_unit: exp}
        duration = timedelta(**kwargs)
        real_exp = int((now + duration).timestamp())
        return real_exp


class BaseBuilder(type):
    def __new__(  # type: ignore
        cls, name: str, bases: Sequence[Any], attrs: Dict[Any, Any]
    ) -> Type["BaseBuilder"]:
        attrs["_payloads"] = [
            key for key, value in attrs.items() if isinstance(value, PayloadDesc)
        ]
        return super().__new__(cls, name, bases, attrs)  # type: ignore


class Builder(metaclass=BaseBuilder):
    _payloads: Sequence[str]

    def __init__(self, client: Any, data: Any) -> None:
        self.client = client
        self.data = data

    def get_payload(self) -> Dict[str, Any]:
        payloads = {}
        for payload in self._payloads:
            payloads[payload] = getattr(self, payload)

        return payloads


class JWTEncoder:
    payload_builder_class: Type["Builder"]
    stage: str = "stg"

    def __init__(self, client: Any) -> None:
        self.client = client

    @property
    def key_url(self) -> str:
        if self.stage == "stg":
            return STG_CERT_URL
        return CERT_URL

    def get_private_key(self) -> str:
        keys = requests.get(self.key_url).json()["keys"]
        key = random.choice(keys)
        return key["kid"]  # type: ignore

    def build_payload(self, data: Any) -> Dict[str, Any]:
        builder = self.payload_builder_class(client=self.client, data=data)
        return builder.get_payload()

    def encode(self, user: Any) -> str:
        key = self.get_private_key()
        data = self.build_payload(user)
        headers = {"kid": key}
        encoded = encode(data, key=key, algorithm="RS256", headers=headers)
        return encoded
