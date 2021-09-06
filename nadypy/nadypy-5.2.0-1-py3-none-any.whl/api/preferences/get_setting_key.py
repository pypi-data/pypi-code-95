from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...types import Response


def _get_kwargs(
    key: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/setting/{key}".format(client.base_url, key=key)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, str]]:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200
    if response.status_code == 204:
        response_204 = None

        return response_204
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, str]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    key: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, str]]:
    kwargs = _get_kwargs(
        key=key,
        client=client,
    )

    response = client.client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, str]]:
    """Get the value of a setting"""

    return sync_detailed(
        key=key,
        client=client,
    ).parsed


async def asyncio_detailed(
    key: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, str]]:
    kwargs = _get_kwargs(
        key=key,
        client=client,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, str]]:
    """Get the value of a setting"""

    return (
        await asyncio_detailed(
            key=key,
            client=client,
        )
    ).parsed
