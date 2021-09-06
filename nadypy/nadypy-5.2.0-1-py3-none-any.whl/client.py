from base64 import b64encode
from time import time_ns
from typing import Dict

import attr
import httpx
from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign


@attr.s(auto_attribs=True)
class Client:
    """A class for keeping track of data related to the API"""

    base_url: str
    headers: Dict[str, str] = attr.ib(factory=dict, kw_only=True)
    timeout: float = attr.ib(5.0, kw_only=True)

    client: httpx.Client = attr.ib(factory=httpx.Client, init=False)
    async_client: httpx.AsyncClient = attr.ib(factory=httpx.AsyncClient, init=False)

    async def close(self) -> None:
        await self.async_client.aclose()

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def with_headers(self, headers: Dict[str, str]) -> "Client":
        """Get a new client matching this one with additional headers"""
        return attr.evolve(self, headers={**self.headers, **headers})

    def get_timeout(self) -> float:
        return self.timeout

    def with_timeout(self, timeout: float) -> "Client":
        """Get a new client matching this one with a new timeout (in seconds)"""
        return attr.evolve(self, timeout=timeout)


class AuthenticatedClient(Client):
    pass


@attr.s(auto_attribs=True)
class BasicAuthClient(AuthenticatedClient):
    """A Client which has been authenticated for use on secured endpoints"""

    username: str
    password: str

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        basic_auth = b64encode(f"{self.username}:{self.password}".encode()).decode("ascii")
        return {"Authorization": f"Basic {basic_auth}", **self.headers}


@attr.s(auto_attribs=True)
class SignedAuthClient(AuthenticatedClient):
    """A Client which has been authenticated for use on secured endpoints"""

    key_id: str
    private_key: str

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        request_id = f"{time_ns() // 1000000}"
        key = load_privatekey(FILETYPE_PEM, self.private_key)
        signature = b64encode(sign(key, request_id.encode(), "sha512")).decode("ascii")
        header_value = f'keyId="{self.key_id}",algorithm="sha512",sequence="{request_id}",signature="{signature}"'
        return {"Signature": header_value, **self.headers}
