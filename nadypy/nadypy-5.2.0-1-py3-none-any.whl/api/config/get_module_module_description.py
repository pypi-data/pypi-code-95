from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...types import Response


def _get_kwargs(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/module/{module}/description".format(client.base_url, module=module)

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
    module: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, str]]:
    kwargs = _get_kwargs(
        module=module,
        client=client,
    )

    response = client.client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, str]]:
    """Get the description of a module"""

    return sync_detailed(
        module=module,
        client=client,
    ).parsed


async def asyncio_detailed(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, str]]:
    kwargs = _get_kwargs(
        module=module,
        client=client,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, str]]:
    """Get the description of a module"""

    return (
        await asyncio_detailed(
            module=module,
            client=client,
        )
    ).parsed
