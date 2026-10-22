from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.focus_session import FocusSession
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    note: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["note"] = note

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/focus/{id}/stop".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FocusSession | None:
    if response.status_code == 200:
        response_200 = FocusSession.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[FocusSession]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    note: str | Unset = UNSET,
) -> Response[FocusSession]:
    """
    Args:
        id (int):
        note (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FocusSession]
    """

    kwargs = _get_kwargs(
        id=id,
        note=note,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    note: str | Unset = UNSET,
) -> FocusSession | None:
    """
    Args:
        id (int):
        note (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FocusSession
    """

    return sync_detailed(
        id=id,
        client=client,
        note=note,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    note: str | Unset = UNSET,
) -> Response[FocusSession]:
    """
    Args:
        id (int):
        note (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FocusSession]
    """

    kwargs = _get_kwargs(
        id=id,
        note=note,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    note: str | Unset = UNSET,
) -> FocusSession | None:
    """
    Args:
        id (int):
        note (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FocusSession
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            note=note,
        )
    ).parsed
