from typing import Any, Dict

import httpx

from ...client import AuthenticatedClient
from ...models.operation import Operation
from ...types import Response


def _get_kwargs(
    module: str,
    event: str,
    handler: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Dict[str, Any]:
    url = "{}/module/{module}/events/{event}/{handler}".format(
        client.base_url, module=module, event=event, handler=handler
    )

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
    event: str,
    handler: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Response[Any]:
    kwargs = _get_kwargs(
        module=module,
        event=event,
        handler=handler,
        client=client,
        json_body=json_body,
    )

    response = client.client.put(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    module: str,
    event: str,
    handler: str,
    *,
    client: AuthenticatedClient,
    json_body: Operation,
) -> Response[Any]:
    kwargs = _get_kwargs(
        module=module,
        event=event,
        handler=handler,
        client=client,
        json_body=json_body,
    )

    response = await client.async_client.put(**kwargs)

    return _build_response(response=response)
