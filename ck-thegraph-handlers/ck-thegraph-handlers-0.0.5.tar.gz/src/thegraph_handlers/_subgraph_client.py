from types import TracebackType
from typing import Any, Dict, Optional, Type

from thegraph_handlers._exceptions import SubgraphError
from thegraph_handlers._protocols import AClosableHTTPClient, Response


class SubgraphClient:
    """
    Client for fetching data from https://thegraph.com/

    Recommended usage is to scope it in a async context manager to properly close
    all connections, like this:

    async with SubgraphAsyncClient(...) as client:
        ...

    `SubgraphClient` is independent of the underlying HTTP client used - be it
    `httpx.AsyncClient` (preferred), `aiohttp.ClientSession` or other. It must just
    conform to the `AClosableHTTPClient` interface.
    """

    def __init__(self, subgraph_url: str, client: AClosableHTTPClient) -> None:
        self._subgraph_url = subgraph_url
        self._client = client

    async def __aenter__(self) -> "SubgraphClient":
        self._client = await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        try:
            await self._client.aclose()
        except AttributeError:
            # 2021/06/24 - aiohttp 3.7.4.post0
            # `aiohttp.ClientSession `implements `__aenter__` and `__aexit__`,
            # but does not implement the `contextlib.aclosing` protocol, ie.
            # its closing coroutine is `close`, not `aclose`.
            await self._client.close()

    async def execute(self, query: str, variables: Optional[dict] = None) -> dict:
        request_data: Dict[str, Any] = {"query": query}
        if variables is not None:
            request_data["variables"] = variables

        response: Response = await self._client.post(
            url=self._subgraph_url, json=request_data
        )

        # Raises an error if response has 400-599 status, otherwise a no-op
        response.raise_for_status()

        response_json = response.json()
        if "errors" in response_json:
            raise SubgraphError(response_json["errors"])
        else:
            return response_json["data"]
