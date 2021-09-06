from typing import Any, Dict

import httpx

from ...client import AuthenticatedClient
from ...models.operation import Operation
from ...types import Response


def _get_kwargs(
    module: str,
    command: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Dict[str, Any]:
    url = "{}/module/{module}/commands/{command}".format(client.base_url, module=module, command=command)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    module: str,
    command: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Response[Any]:
    kwargs = _get_kwargs(
        module=module,
        command=command,
        client=client,
        json_body=json_body,
    )

    response = client.client.patch(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    module: str,
    command: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Response[Any]:
    kwargs = _get_kwargs(
        module=module,
        command=command,
        client=client,
        json_body=json_body,
    )

    response = await client.async_client.patch(**kwargs)

    return _build_response(response=response)
