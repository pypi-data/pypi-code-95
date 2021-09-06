from __future__ import annotations

import typing

import asyncio
import aiohttp

import logging

from .utils import MISSING
from .auth import Authentication

from .objects import BaseObject

logger = logging.getLogger(__name__)

__all__ = ("HTTPClient",)

T = typing.TypeVar("T", bound=BaseObject)


class HTTPClient:
    """
    Used to handle everything related to making requests and handling them.

    Attributes:
        session (aiohttp.ClientSession): The ClientSession to use for requests
        auth (Authentication): The authentication regarding the current user

    """

    BASE: typing.ClassVar[str] = "https://osu.ppy.sh/api/v2"

    def __init__(
        self, auth: Authentication, session: aiohttp.ClientSession = MISSING
    ) -> None:
        self.session: aiohttp.ClientSession = session
        self.auth: Authentication = auth

        self._lock = asyncio.Lock()

    def url(self, endpoint: str) -> str:
        """
        Makes the full url for the request.

        Args:
            endpoint (str): The endpoint

        Returns:
            The full url for the request

        """
        return f"{self.BASE}{endpoint}"

    async def _create_session(
        self, loop: typing.Optional[asyncio.AbstractEventLoop] = MISSING
    ) -> aiohttp.ClientSession:
        """
        Here to create the ClientSession in an async method

        Args:
            loop (typing.Optional[asyncio.AbstractEventLoop]): The loop to use for this ClientSession. Defaults to None.

        Returns:
            The created ClientSession
        """
        return aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())

    async def handle_parse(
        self, resp: aiohttp.ClientResponse, *, cls: typing.Type[T], **kwargs
    ) -> typing.Optional[T]:
        data = await resp.json()

        if "error" in data:
            return None

        return cls(data, **kwargs)

    async def request(
        self, method: str, url: str, *args, **kwargs
    ) -> aiohttp.ClientResponse:
        """
        A method used to make a request

        Args:
            method (str): Which method to use
            url (str): The url to send the request to

        Returns:
            The ClientResponse of the request
        """
        if not self.session:
            self.session = await self._create_session()

        async with self._lock:
            resp = await self.session.request(method, url, *args, **kwargs)

        # Lock was here originally because I was gonna handle ratelimits.
        # But who in their right mind would send 1200 requests in a small period?????
        # If you get ratelimited thats on you

        return resp

    async def login(self) -> None:
        payload = {
            "client_id": self.auth["client_id"],
            "client_secret": self.auth["client_secret"],
            "grant_type": "client_credentials",
            "scope": "public",
        }
        resp = await self.request(
            "POST", "https://osu.ppy.sh/oauth/token", json=payload
        )
        data = await resp.json()

        self.session.headers["Authorization"] = f"Bearer {data['access_token']}"
        self.auth["token"] = data
