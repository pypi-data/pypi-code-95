from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.relay_status import RelayStatus
from ...types import Response


def _get_kwargs(
    relay: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/relay/{relay}/status".format(client.base_url, relay=relay)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, RelayStatus]]:
    if response.status_code == 200:
        response_200 = RelayStatus.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = None

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, RelayStatus]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    relay: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, RelayStatus]]:
    kwargs = _get_kwargs(
        relay=relay,
        client=client,
    )

    response = client.client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    relay: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, RelayStatus]]:
    """Get a relay's status"""

    return sync_detailed(
        relay=relay,
        client=client,
    ).parsed


async def asyncio_detailed(
    relay: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, RelayStatus]]:
    kwargs = _get_kwargs(
        relay=relay,
        client=client,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    relay: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, RelayStatus]]:
    """Get a relay's status"""

    return (
        await asyncio_detailed(
            relay=relay,
            client=client,
        )
    ).parsed
