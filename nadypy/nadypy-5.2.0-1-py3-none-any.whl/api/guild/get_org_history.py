from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.org_history import OrgHistory
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = UNSET,
    actor: Union[Unset, None, str] = UNSET,
    actee: Union[Unset, None, str] = UNSET,
    action: Union[Unset, None, str] = UNSET,
    before: Union[Unset, None, int] = UNSET,
    after: Union[Unset, None, int] = UNSET,
) -> Dict[str, Any]:
    url = "{}/org/history".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {
        "limit": limit,
        "actor": actor,
        "actee": actee,
        "action": action,
        "before": before,
        "after": after,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[OrgHistory]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = OrgHistory.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[OrgHistory]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = UNSET,
    actor: Union[Unset, None, str] = UNSET,
    actee: Union[Unset, None, str] = UNSET,
    action: Union[Unset, None, str] = UNSET,
    before: Union[Unset, None, int] = UNSET,
    after: Union[Unset, None, int] = UNSET,
) -> Response[List[OrgHistory]]:
    kwargs = _get_kwargs(
        client=client,
        limit=limit,
        actor=actor,
        actee=actee,
        action=action,
        before=before,
        after=after,
    )

    response = client.client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = UNSET,
    actor: Union[Unset, None, str] = UNSET,
    actee: Union[Unset, None, str] = UNSET,
    action: Union[Unset, None, str] = UNSET,
    before: Union[Unset, None, int] = UNSET,
    after: Union[Unset, None, int] = UNSET,
) -> Optional[List[OrgHistory]]:
    """Query entries from the org history log"""

    return sync_detailed(
        client=client,
        limit=limit,
        actor=actor,
        actee=actee,
        action=action,
        before=before,
        after=after,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = UNSET,
    actor: Union[Unset, None, str] = UNSET,
    actee: Union[Unset, None, str] = UNSET,
    action: Union[Unset, None, str] = UNSET,
    before: Union[Unset, None, int] = UNSET,
    after: Union[Unset, None, int] = UNSET,
) -> Response[List[OrgHistory]]:
    kwargs = _get_kwargs(
        client=client,
        limit=limit,
        actor=actor,
        actee=actee,
        action=action,
        before=before,
        after=after,
    )

    response = await client.async_client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = UNSET,
    actor: Union[Unset, None, str] = UNSET,
    actee: Union[Unset, None, str] = UNSET,
    action: Union[Unset, None, str] = UNSET,
    before: Union[Unset, None, int] = UNSET,
    after: Union[Unset, None, int] = UNSET,
) -> Optional[List[OrgHistory]]:
    """Query entries from the org history log"""

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            actor=actor,
            actee=actee,
            action=action,
            before=before,
            after=after,
        )
    ).parsed
