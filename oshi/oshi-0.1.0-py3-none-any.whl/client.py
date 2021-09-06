from __future__ import annotations

import typing

import aiohttp

from .auth import Authentication
from .http import HTTPClient
from .utils import MISSING

from .objects import Beatmap


__all__ = ("Client",)


class Client:
    def __init__(
        self, auth: Authentication, *, session: aiohttp.ClientSession = MISSING
    ):
        self.http = HTTPClient(auth=auth, session=session)
        self.auth: Authentication = auth

    def __repr__(self) -> str:
        return f"<Client ID={self.auth['client_id']}>"

    async def __aenter__(self) -> Client:
        await self.login()
        return self

    async def __aexit__(self, *_) -> None:
        return await self.close()

    async def login(self) -> None:
        return await self.http.login()

    async def close(self) -> None:
        return await self.http.session.close()

    async def get_beatmap(
        self, id: int = MISSING, checksum: str = MISSING, filename: str = MISSING
    ) -> typing.Optional[Beatmap]:
        payload = {
            "id": id or None,
            "filename": filename or None,
            "checksum": checksum or None,
        }
        resp = await self.http.request(
            "GET", (self.http.url("/beatmaps/lookup")), json=payload
        )

        return await self.http.handle_parse(resp, cls=Beatmap)
