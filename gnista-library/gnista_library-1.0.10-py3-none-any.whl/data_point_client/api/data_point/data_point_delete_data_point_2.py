from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
) -> Dict[str, Any]:
    url = "{}/DataPoint/tenant/{tenantName}/{dataPointId}".format(
        client.base_url, dataPointId=data_point_id, tenantName=tenant_name
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[ProblemDetails]:
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[ProblemDetails]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
) -> Response[ProblemDetails]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
    )

    response = httpx.delete(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
) -> Optional[ProblemDetails]:
    """ """

    return sync_detailed(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
) -> Response[ProblemDetails]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
) -> Optional[ProblemDetails]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            data_point_id=data_point_id,
            tenant_name=tenant_name,
        )
    ).parsed
