from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.draft_files_read_entry import DraftFilesReadEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    filename: str,
    *,
    client: Client,
    content_type: Union[Unset, str] = "application/octet-stream",
) -> Dict[str, Any]:
    url = "{}/records/{id}/draft/files/{filename}/content".format(
        client.base_url, id=id, filename=filename
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if content_type is not UNSET:
        headers["content-type"] = content_type

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
    content_type: Union[Unset, str] = "application/octet-stream",
) -> Response[DraftFilesReadEntry]:
    kwargs = _get_kwargs(
        id=id,
        filename=filename,
        client=client,
        content_type=content_type,
    )

    response = httpx.put(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    filename: str,
    *,
    client: Client,
    content_type: Union[Unset, str] = "application/octet-stream",
) -> Optional[DraftFilesReadEntry]:
    """  """

    return sync_detailed(
        id=id,
        filename=filename,
        client=client,
        content_type=content_type,
    ).parsed


async def asyncio_detailed(
    id: str,
    filename: str,
    *,
    client: Client,
    content_type: Union[Unset, str] = "application/octet-stream",
) -> Response[DraftFilesReadEntry]:
    kwargs = _get_kwargs(
        id=id,
        filename=filename,
        client=client,
        content_type=content_type,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.put(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    filename: str,
    *,
    client: Client,
    content_type: Union[Unset, str] = "application/octet-stream",
) -> Optional[DraftFilesReadEntry]:
    """  """

    return (
        await asyncio_detailed(
            id=id,
            filename=filename,
            client=client,
            content_type=content_type,
        )
    ).parsed
