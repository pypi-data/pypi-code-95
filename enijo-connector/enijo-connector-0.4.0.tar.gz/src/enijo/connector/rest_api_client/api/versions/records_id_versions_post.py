from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.record_read import RecordRead
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/records/{id}/versions".format(client.base_url, id=id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[RecordRead]:
    if response.status_code == 201:
        response_201 = RecordRead.from_dict(response.json())

        return response_201
    return None


def _build_response(*, response: httpx.Response) -> Response[RecordRead]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: Client,
) -> Response[RecordRead]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    *,
    client: Client,
) -> Optional[RecordRead]:
    """Each record has a draft associated with it. This operation retrieves the draft record of a record.

    If the draft record of a record has not been created yet, it is created."""

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: Client,
) -> Response[RecordRead]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: Client,
) -> Optional[RecordRead]:
    """Each record has a draft associated with it. This operation retrieves the draft record of a record.

    If the draft record of a record has not been created yet, it is created."""

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
