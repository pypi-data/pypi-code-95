from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.module_command import ModuleCommand
from ...models.module_subcommand_channel import ModuleSubcommandChannel
from ...types import Response


def _get_kwargs(
    module: str,
    command: str,
    channel: str,
    *,
    client: AuthenticatedClient,
    json_body: ModuleSubcommandChannel,
) -> Dict[str, Any]:
    url = "{}/module/{module}/commands/{command}/{channel}".format(
        client.base_url, module=module, command=command, channel=channel
    )

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, ModuleCommand]]:
    if response.status_code == 200:
        response_200 = ModuleCommand.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = None

        return response_422
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, ModuleCommand]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    module: str,
    command: str,
    channel: str,
    *,
    client: AuthenticatedClient,
    json_body: ModuleSubcommandChannel,
) -> Response[Union[Any, ModuleCommand]]:
    kwargs = _get_kwargs(
        module=module,
        command=command,
        channel=channel,
        client=client,
        json_body=json_body,
    )

    response = client.client.put(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    module: str,
    command: str,
    channel: str,
    *,
    client: AuthenticatedClient,
    json_body: ModuleSubcommandChannel,
) -> Optional[Union[Any, ModuleCommand]]:
    """Activate or deactivate a Command"""

    return sync_detailed(
        module=module,
        command=command,
        channel=channel,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    module: str,
    command: str,
    channel: str,
    *,
    client: AuthenticatedClient,
    json_body: ModuleSubcommandChannel,
) -> Response[Union[Any, ModuleCommand]]:
    kwargs = _get_kwargs(
        module=module,
        command=command,
        channel=channel,
        client=client,
        json_body=json_body,
    )

    response = await client.async_client.put(**kwargs)

    return _build_response(response=response)


async def asyncio(
    module: str,
    command: str,
    channel: str,
    *,
    client: AuthenticatedClient,
    json_body: ModuleSubcommandChannel,
) -> Optional[Union[Any, ModuleCommand]]:
    """Activate or deactivate a Command"""

    return (
        await asyncio_detailed(
            module=module,
            command=command,
            channel=channel,
            client=client,
            json_body=json_body,
        )
    ).parsed
