from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.data_point_response_base import DataPointResponseBase
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    version: int,
) -> Dict[str, Any]:
    url = "{}/DataPoint/tenant/{tenantName}/{dataPointId}/{version}".format(
        client.base_url, dataPointId=data_point_id, tenantName=tenant_name, version=version
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[DataPointResponseBase, ProblemDetails]]:
    if response.status_code == 200:
        response_200 = DataPointResponseBase.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[DataPointResponseBase, ProblemDetails]]:
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
    version: int,
) -> Response[Union[DataPointResponseBase, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        version=version,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    version: int,
) -> Optional[Union[DataPointResponseBase, ProblemDetails]]:
    """ """

    return sync_detailed(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        version=version,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    version: int,
) -> Response[Union[DataPointResponseBase, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        version=version,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    version: int,
) -> Optional[Union[DataPointResponseBase, ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            data_point_id=data_point_id,
            tenant_name=tenant_name,
            version=version,
        )
    ).parsed
