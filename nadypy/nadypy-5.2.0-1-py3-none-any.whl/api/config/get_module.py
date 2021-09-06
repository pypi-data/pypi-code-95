from typing import Any, Dict, List, Optional

import httpx

from ...client import AuthenticatedClient
from ...models.config_module import ConfigModule
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/module".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ConfigModule]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ConfigModule.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ConfigModule]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[List[ConfigModule]]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = client.client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[List[ConfigModule]]:
    """Get a list of available modules to configure"""

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[List[ConfigModule]]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[List[ConfigModule]]:
    """Get a list of available modules to configure"""

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
