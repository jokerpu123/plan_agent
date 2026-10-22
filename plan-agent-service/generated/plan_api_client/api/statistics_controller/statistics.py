from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.statistics_result import StatisticsResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    email: str,
    from_: str,
    to: str,
    plan_type: str | Unset = "daily",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["email"] = email

    params["from"] = from_

    params["to"] = to

    params["planType"] = plan_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/statistics",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> StatisticsResult | None:
    if response.status_code == 200:
        response_200 = StatisticsResult.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[StatisticsResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    from_: str,
    to: str,
    plan_type: str | Unset = "daily",
) -> Response[StatisticsResult]:
    """
    Args:
        email (str):
        from_ (str):
        to (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[StatisticsResult]
    """

    kwargs = _get_kwargs(
        email=email,
        from_=from_,
        to=to,
        plan_type=plan_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    from_: str,
    to: str,
    plan_type: str | Unset = "daily",
) -> StatisticsResult | None:
    """
    Args:
        email (str):
        from_ (str):
        to (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        StatisticsResult
    """

    return sync_detailed(
        client=client,
        email=email,
        from_=from_,
        to=to,
        plan_type=plan_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    from_: str,
    to: str,
    plan_type: str | Unset = "daily",
) -> Response[StatisticsResult]:
    """
    Args:
        email (str):
        from_ (str):
        to (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[StatisticsResult]
    """

    kwargs = _get_kwargs(
        email=email,
        from_=from_,
        to=to,
        plan_type=plan_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    from_: str,
    to: str,
    plan_type: str | Unset = "daily",
) -> StatisticsResult | None:
    """
    Args:
        email (str):
        from_ (str):
        to (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        StatisticsResult
    """

    return (
        await asyncio_detailed(
            client=client,
            email=email,
            from_=from_,
            to=to,
            plan_type=plan_type,
        )
    ).parsed
