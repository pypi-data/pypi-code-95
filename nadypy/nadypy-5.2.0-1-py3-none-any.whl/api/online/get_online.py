from typing import Any, Dict, Optional

import httpx

from ...client import AuthenticatedClient
from ...models.online_players import OnlinePlayers
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/online".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[OnlinePlayers]:
    if response.status_code == 200:
        response_200 = OnlinePlayers.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[OnlinePlayers]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[OnlinePlayers]:
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
) -> Optional[OnlinePlayers]:
    """Get a list of all people online in all linked channels"""

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[OnlinePlayers]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[OnlinePlayers]:
    """Get a list of all people online in all linked channels"""

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
