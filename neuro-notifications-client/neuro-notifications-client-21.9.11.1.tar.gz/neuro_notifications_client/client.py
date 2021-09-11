import logging
from typing import Any, Mapping, Optional, Sequence

import aiohttp
import aiohttp.web
from aiohttp.client import _RequestContextManager  # eventually will be public
from aiohttp.hdrs import AUTHORIZATION, USER_AGENT
from yarl import URL

from neuro_notifications_client.schema import SLUG_TO_SCHEMA

from .notifications import Notification
from .version import VERSION


logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        url: URL,
        token: str,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ) -> None:
        self._url = url
        self._token = token
        self._trace_configs = list(trace_configs)
        self._client: Optional[aiohttp.ClientSession] = None

    async def init(self) -> None:
        if not self._url:
            return
        if self._client is None:  # pragma: no branch
            self._client = aiohttp.ClientSession(
                raise_for_status=True,
                headers=self._generate_headers(),
                trace_configs=self._trace_configs,
            )

    async def __aenter__(self) -> "Client":
        await self.init()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client is not None:
            client = self._client
            self._client = None
            await client.close()

    def _generate_headers(self) -> Mapping[str, str]:
        headers: Mapping[str, str] = {
            AUTHORIZATION: f"Bearer {self._token}",
            USER_AGENT: f"NotificationsClient/{VERSION}",
        }
        return headers

    def _make_url(self, path: str) -> URL:
        if path.startswith("/"):
            path = path[1:]
        return self._url / path

    def _request(
        self, method: str, path: str, *args: Any, **kwargs: Any
    ) -> _RequestContextManager:
        # Not a coroutine actually but coroutine builder
        # later we'll drop the trick most likely
        url = self._make_url(path)
        return self._client.request(method, url, *args, **kwargs)  # type: ignore

    async def ping(self, timeout_seconds: float = 10) -> None:
        if not self._url:
            return
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        async with self._request("GET", "/api/v1/ping", timeout=timeout) as resp:
            txt = await resp.text()
            assert txt == "Pong"

    async def secured_ping(self, timeout_seconds: float = 10) -> None:
        if not self._url:
            return
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        async with self._request(
            "GET", "/api/v1/secured-ping", timeout=timeout
        ) as resp:
            txt = await resp.text()
            assert txt == "Pong"

    async def notify(self, notification: Notification) -> None:
        if not self._url:
            return
        slug = notification.slug()
        schema_cls = SLUG_TO_SCHEMA.get(slug)
        if schema_cls is None:
            raise ValueError(f"Notification {notification} is not supported")
        payload = schema_cls().dump(notification)
        async with self._request(
            "POST", f"/api/v1/notifications/{slug}", json=payload
        ) as resp:
            if resp.status != aiohttp.web.HTTPCreated.status_code:
                raise RuntimeError("Server return %s instead HTTPCreated", resp.status)
