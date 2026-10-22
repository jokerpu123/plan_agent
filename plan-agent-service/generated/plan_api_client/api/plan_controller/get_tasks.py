from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.task import Task
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    email: str,
    date: str,
    plan_type: str | Unset = "daily",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["email"] = email

    params["date"] = date

    params["planType"] = plan_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/tasks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[Task] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Task.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[Task]]:
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
    date: str,
    plan_type: str | Unset = "daily",
) -> Response[list[Task]]:
    """
    Args:
        email (str):
        date (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Task]]
    """

    kwargs = _get_kwargs(
        email=email,
        date=date,
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
    date: str,
    plan_type: str | Unset = "daily",
) -> list[Task] | None:
    """
    Args:
        email (str):
        date (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Task]
    """

    return sync_detailed(
        client=client,
        email=email,
        date=date,
        plan_type=plan_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    date: str,
    plan_type: str | Unset = "daily",
) -> Response[list[Task]]:
    """
    Args:
        email (str):
        date (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[Task]]
    """

    kwargs = _get_kwargs(
        email=email,
        date=date,
        plan_type=plan_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    email: str,
    date: str,
    plan_type: str | Unset = "daily",
) -> list[Task] | None:
    """
    Args:
        email (str):
        date (str):
        plan_type (str | Unset):  Default: 'daily'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[Task]
    """

    return (
        await asyncio_detailed(
            client=client,
            email=email,
            date=date,
            plan_type=plan_type,
        )
    ).parsed
