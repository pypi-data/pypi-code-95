from asyncio import TimeoutError

import pytest
from aiohttp.client_exceptions import ClientResponseError

from neuro_notifications_client import Client


async def test_ping(client: Client) -> None:
    await client.ping()  # should not raise exception


async def test_ping_with_timeout(client: Client) -> None:
    with pytest.raises(TimeoutError):
        await client.ping(0.1)


async def test_secured_ping(client: Client) -> None:
    await client.secured_ping()  # should not raise exception
    async with Client(client._url, "no-access-token") as no_access_client:
        with pytest.raises(ClientResponseError):
            await no_access_client.secured_ping()


async def test_secured_ping_with_timeout(client: Client) -> None:
    with pytest.raises(TimeoutError):
        await client.secured_ping(0.1)
