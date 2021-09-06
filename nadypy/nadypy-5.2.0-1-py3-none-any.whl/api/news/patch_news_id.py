from typing import Any, Dict, Optional

import httpx

from ...client import AuthenticatedClient
from ...models.new_news import NewNews
from ...models.news import News
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Dict[str, Any]:
    url = "{}/news/{id}".format(client.base_url, id=id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[News]:
    if response.status_code == 200:
        response_200 = News.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[News]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Response[News]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
    )

    response = client.client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Optional[News]:
    """Modify an existing news item"""

    return sync_detailed(
        id=id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Response[News]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        json_body=json_body,
    )

    response = await client.async_client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient,
    json_body: NewNews,
) -> Optional[News]:
    """Modify an existing news item"""

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            json_body=json_body,
        )
    ).parsed
