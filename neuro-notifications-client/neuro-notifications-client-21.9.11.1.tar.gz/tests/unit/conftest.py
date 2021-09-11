import asyncio
from typing import AsyncIterator, Awaitable, Callable

import aiohttp.web
import pytest
from aiohttp.abc import Application
from aiohttp.hdrs import AUTHORIZATION
from aiohttp.test_utils import TestServer as AioHTTPTestServer

from neuro_notifications_client import Client
from neuro_notifications_client.notifications import Notification


@pytest.fixture
def event_loop(loop: asyncio.AbstractEventLoop) -> asyncio.AbstractEventLoop:
    """
    This fixture mitigates the compatibility issues between
    pytest-asyncio and pytest-aiohttp.
    """
    return loop


@pytest.fixture
async def api_server(
    aiohttp_server: Callable[[Application], Awaitable[AioHTTPTestServer]], token: str
) -> AsyncIterator[AioHTTPTestServer]:
    async def _post_notification(request: aiohttp.web.Request) -> aiohttp.web.Response:
        raise aiohttp.web.HTTPCreated()

    async def _unknown_notification(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        raise aiohttp.web.HTTPNotFound()

    async def _strange_notification(
        request: aiohttp.web.Request,
    ) -> aiohttp.web.Response:
        raise aiohttp.web.HTTPOk()

    async def _ping(request: aiohttp.web.Request) -> aiohttp.web.Response:
        await asyncio.sleep(2)
        return aiohttp.web.Response(text="Pong")

    async def _secured_ping(request: aiohttp.web.Request) -> aiohttp.web.Response:
        auth_header = request.headers.get(AUTHORIZATION)
        if auth_header != f"Bearer {token}":
            raise aiohttp.web.HTTPForbidden
        await asyncio.sleep(2)
        return aiohttp.web.Response(text="Pong")

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get("/api/v1/ping", _ping)])
    app.add_routes([aiohttp.web.get("/api/v1/secured-ping", _secured_ping)])

    app.add_routes(
        [aiohttp.web.post("/api/v1/notifications/unknown", _unknown_notification)]
    )
    app.add_routes(
        [aiohttp.web.post("/api/v1/notifications/{type}", _post_notification)]
    )
    server = await aiohttp_server(app)
    yield server


@pytest.fixture
def token() -> str:
    return "secured-token"


@pytest.fixture
async def client(api_server: AioHTTPTestServer, token: str) -> AsyncIterator[Client]:

    async with Client(api_server.make_url(""), token=token) as client:
        yield client


@pytest.fixture
def unknown_notification() -> Notification:
    class UnknownNotification(Notification):
        @classmethod
        def slug(cls) -> str:
            return "unknown"

    return UnknownNotification()
