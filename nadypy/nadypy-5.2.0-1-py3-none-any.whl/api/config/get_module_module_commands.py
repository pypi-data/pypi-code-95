from typing import Any, Dict, List, Optional

import httpx

from ...client import AuthenticatedClient
from ...models.module_command import ModuleCommand
from ...types import Response


def _get_kwargs(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/module/{module}/commands".format(client.base_url, module=module)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ModuleCommand]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ModuleCommand.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ModuleCommand]]:
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
) -> Response[List[ModuleCommand]]:
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
) -> Optional[List[ModuleCommand]]:
    """Get a list of available commands for a module"""

    return sync_detailed(
        module=module,
        client=client,
    ).parsed


async def asyncio_detailed(
    module: str,
    *,
    client: AuthenticatedClient,
) -> Response[List[ModuleCommand]]:
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
) -> Optional[List[ModuleCommand]]:
    """Get a list of available commands for a module"""

    return (
        await asyncio_detailed(
            module=module,
            client=client,
        )
    ).parsed
