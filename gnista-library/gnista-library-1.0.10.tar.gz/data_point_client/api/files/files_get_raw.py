from io import BytesIO
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.problem_details import ProblemDetails
from ...types import File, Response


def _get_kwargs(
    *,
    client: Client,
    file_id: str,
) -> Dict[str, Any]:
    url = "{}/Files/{fileId}/raw".format(client.base_url, fileId=file_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[File, ProblemDetails]]:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[File, ProblemDetails]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    file_id: str,
) -> Response[Union[File, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        file_id=file_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    file_id: str,
) -> Optional[Union[File, ProblemDetails]]:
    """ """

    return sync_detailed(
        client=client,
        file_id=file_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    file_id: str,
) -> Response[Union[File, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        file_id=file_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    file_id: str,
) -> Optional[Union[File, ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            file_id=file_id,
        )
    ).parsed
