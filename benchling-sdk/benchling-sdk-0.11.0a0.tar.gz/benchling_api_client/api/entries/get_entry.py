from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.entry_by_id import EntryById
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    entry_id: str,
) -> Dict[str, Any]:
    url = "{}/entries/{entry_id}".format(client.base_url, entry_id=entry_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[EntryById]:
    if response.status_code == 200:
        response_200 = EntryById.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[EntryById]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entry_id: str,
) -> Response[EntryById]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entry_id: str,
) -> Optional[EntryById]:
    """ Get a notebook entry by ID """

    return sync_detailed(
        client=client,
        entry_id=entry_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entry_id: str,
) -> Response[EntryById]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entry_id: str,
) -> Optional[EntryById]:
    """ Get a notebook entry by ID """

    return (
        await asyncio_detailed(
            client=client,
            entry_id=entry_id,
        )
    ).parsed
