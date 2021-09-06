from typing import Any, Dict

import httpx

from ...client import AuthenticatedClient
from ...models.new_news import NewNews
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Dict[str, Any]:
    url = "{}/news".format(client.base_url)

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
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Response[Any]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = client.client.post(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Response[Any]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = await client.async_client.post(**kwargs)

    return _build_response(response=response)
