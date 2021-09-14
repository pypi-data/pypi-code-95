import datetime
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.get_data_response import GetDataResponse
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    window_hours: Union[Unset, int] = UNSET,
    version: Union[Unset, None, int] = UNSET,
    from_date: Union[Unset, None, datetime.datetime] = UNSET,
    to_date: Union[Unset, None, datetime.datetime] = UNSET,
    unit: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/DataPoint/tenant/{tenantName}/{dataPointId}/data".format(
        client.base_url, dataPointId=data_point_id, tenantName=tenant_name
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_from_date: Union[Unset, None, str] = UNSET
    if not isinstance(from_date, Unset):
        json_from_date = from_date.isoformat() if from_date else None

    json_to_date: Union[Unset, None, str] = UNSET
    if not isinstance(to_date, Unset):
        json_to_date = to_date.isoformat() if to_date else None

    params: Dict[str, Any] = {
        "windowHours": window_hours,
        "version": version,
        "fromDate": json_from_date,
        "toDate": json_to_date,
        "unit": unit,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
        "verify": False,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    if response.status_code == 200:
        response_200 = GetDataResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[GetDataResponse, ProblemDetails]]:
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
    window_hours: Union[Unset, int] = UNSET,
    version: Union[Unset, None, int] = UNSET,
    from_date: Union[Unset, None, datetime.datetime] = UNSET,
    to_date: Union[Unset, None, datetime.datetime] = UNSET,
    unit: Union[Unset, None, str] = UNSET,
) -> Response[Union[GetDataResponse, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        window_hours=window_hours,
        version=version,
        from_date=from_date,
        to_date=to_date,
        unit=unit,
    )

    response = httpx.get(**kwargs)

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    window_hours: Union[Unset, int] = UNSET,
    version: Union[Unset, None, int] = UNSET,
    from_date: Union[Unset, None, datetime.datetime] = UNSET,
    to_date: Union[Unset, None, datetime.datetime] = UNSET,
    unit: Union[Unset, None, str] = UNSET,
) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    """ """

    return sync_detailed(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        window_hours=window_hours,
        version=version,
        from_date=from_date,
        to_date=to_date,
        unit=unit,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    window_hours: Union[Unset, int] = UNSET,
    version: Union[Unset, None, int] = UNSET,
    from_date: Union[Unset, None, datetime.datetime] = UNSET,
    to_date: Union[Unset, None, datetime.datetime] = UNSET,
    unit: Union[Unset, None, str] = UNSET,
) -> Response[Union[GetDataResponse, ProblemDetails]]:
    kwargs = _get_kwargs(
        client=client,
        data_point_id=data_point_id,
        tenant_name=tenant_name,
        window_hours=window_hours,
        version=version,
        from_date=from_date,
        to_date=to_date,
        unit=unit,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    data_point_id: str,
    tenant_name: Optional[str],
    window_hours: Union[Unset, int] = UNSET,
    version: Union[Unset, None, int] = UNSET,
    from_date: Union[Unset, None, datetime.datetime] = UNSET,
    to_date: Union[Unset, None, datetime.datetime] = UNSET,
    unit: Union[Unset, None, str] = UNSET,
) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            data_point_id=data_point_id,
            tenant_name=tenant_name,
            window_hours=window_hours,
            version=version,
            from_date=from_date,
            to_date=to_date,
            unit=unit,
        )
    ).parsed
