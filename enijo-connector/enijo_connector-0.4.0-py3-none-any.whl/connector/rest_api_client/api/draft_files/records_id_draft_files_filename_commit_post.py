from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.draft_files_read_entry import DraftFilesReadEntry
from ...types import Response


def _get_kwargs(
    id: str,
    filename: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/records/{id}/draft/files/{filename}/commit".format(
        client.base_url, id=id, filename=filename
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[DraftFilesReadEntry]:
    if response.status_code == 200:
        response_200 = DraftFilesReadEntry.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[DraftFilesReadEntry]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: str,
    filename: str,
    *,
    client: Client,
) -> Response[DraftFilesReadEntry]:
    kwargs = _get_kwargs(
        id=id,
        filename=filename,
        client=client,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    filename: str,
    *,
    client: Client,
) -> Optional[DraftFilesReadEntry]:
    """  """

    return sync_detailed(
        id=id,
        filename=filename,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    filename: str,
    *,
    client: Client,
) -> Response[DraftFilesReadEntry]:
    kwargs = _get_kwargs(
        id=id,
        filename=filename,
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    filename: str,
    *,
    client: Client,
) -> Optional[DraftFilesReadEntry]:
    """  """

    return (
        await asyncio_detailed(
            id=id,
            filename=filename,
            client=client,
        )
    ).parsed
