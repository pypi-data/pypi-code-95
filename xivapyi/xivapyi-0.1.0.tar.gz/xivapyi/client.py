import asyncio
import atexit
import typing as t

from aiohttp import ClientResponse, ClientSession

from xivapyi import errors

__all__: t.List[str] = [
    "Client",
]


class Client:
    """Async client with helper methods for making calls to the XIVAPI.

    Args:
        token: str
            The XIVAPI api key to use for requests.
        session: Optional[aiohttp.ClientSession]
            The Client Session to use for requests. Defaults to
            None. If no Client Session is passed, one will be
            created.
    """

    __slots__: t.Sequence[str] = ("_loop", "_url", "_session", "_params")

    def __init__(self, token: str, *, session: t.Optional[ClientSession] = None) -> None:
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._params: t.Dict[str, str] = {"private_key": token}
        self._url: str = "https://xivapi.com"

        if isinstance(session, ClientSession):
            self._session = session
        else:
            self._session = ClientSession()
            atexit.register(self.close)

    @property
    def session(self) -> ClientSession:
        """The Client Session used for web requests."""
        if self._session.closed:
            self._session = ClientSession()

        return self._session

    @property
    def url(self) -> str:
        """The base url for the XIVAPI."""
        return self._url

    def close(self) -> None:
        """Closes down the in use Client Session.

        This function is scheduled to run automatically on program
        exit if no Client Session is passed during the Client
        instantiation (It can be called manually as well).

        If an external Client Session is passed however, this function
        will not be scheduled to preserve the integrity of your
        existing Client Session.
        """
        if isinstance(self._session, ClientSession):
            if not self._session.closed:
                self._loop.run_until_complete(self._session.close())

    async def get_item_by_id(
        self,
        item_id: int,
        *,
        columns: t.Optional[t.Iterable[str]] = None,
    ) -> t.Dict[t.Any, t.Any]:
        """Request information on an item by it's ID.

        Args:
            item_id: int
                The item ID of the item to search for.
            columns: Optional[Iterable[str]]
                The columns of data to retrieve. Useful for filtering
                out unneeded data.

        Raises:
            FailedRequest: Raised when a non 200 response is received
            from XIVAPI.

        Returns:
            Dict[Any, Any]: The requested data.
        """
        uri = f"/item/{item_id}"
        params = self._params.copy()

        if columns:
            params["columns"] = ",".join(columns)

        async with self.session.get(self.url + uri, params=params) as resp:
            return await self._deserialize(resp)

    @staticmethod
    async def _deserialize(response: ClientResponse) -> t.Dict[t.Any, t.Any]:
        """Internal method for decoding the response from XIVAPI."""
        data: t.Dict[t.Any, t.Any] = await response.json()

        if 200 <= response.status <= 299:
            return data

        raise errors.FailedRequest(
            f"Response status -> {data['ExCode']} | Info -> {data['Message']}"
        )
