from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.focus_session_status import FocusSessionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task import Task
    from ..models.user import User


T = TypeVar("T", bound="FocusSession")


@_attrs_define
class FocusSession:
    """
    Attributes:
        id (int | Unset):
        user (User | Unset):
        task (Task | Unset):
        title (str | Unset):
        started_at (datetime.datetime | Unset):
        ended_at (datetime.datetime | None | Unset):
        duration_seconds (int | None | Unset):
        status (FocusSessionStatus | Unset):
        note (None | str | Unset):
    """

    id: int | Unset = UNSET
    user: User | Unset = UNSET
    task: Task | Unset = UNSET
    title: str | Unset = UNSET
    started_at: datetime.datetime | Unset = UNSET
    ended_at: datetime.datetime | None | Unset = UNSET
    duration_seconds: int | None | Unset = UNSET
    status: FocusSessionStatus | Unset = UNSET
    note: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        task: dict[str, Any] | Unset = UNSET
        if not isinstance(self.task, Unset):
            task = self.task.to_dict()

        title = self.title

        started_at: str | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        ended_at: None | str | Unset
        if isinstance(self.ended_at, Unset):
            ended_at = UNSET
        elif isinstance(self.ended_at, datetime.datetime):
            ended_at = self.ended_at.isoformat()
        else:
            ended_at = self.ended_at

        duration_seconds: int | None | Unset
        if isinstance(self.duration_seconds, Unset):
            duration_seconds = UNSET
        else:
            duration_seconds = self.duration_seconds

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if user is not UNSET:
            field_dict["user"] = user
        if task is not UNSET:
            field_dict["task"] = task
        if title is not UNSET:
            field_dict["title"] = title
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if ended_at is not UNSET:
            field_dict["endedAt"] = ended_at
        if duration_seconds is not UNSET:
            field_dict["durationSeconds"] = duration_seconds
        if status is not UNSET:
            field_dict["status"] = status
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.task import Task
        from ..models.user import User

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _user = d.pop("user", UNSET)
        user: User | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = User.from_dict(_user)

        _task = d.pop("task", UNSET)
        task: Task | Unset
        if isinstance(_task, Unset):
            task = UNSET
        else:
            task = Task.from_dict(_task)

        title = d.pop("title", UNSET)

        _started_at = d.pop("startedAt", UNSET)
        started_at: datetime.datetime | Unset
        if isinstance(_started_at, Unset):
            started_at = UNSET
        else:
            started_at = datetime.datetime.fromisoformat(_started_at)

        def _parse_ended_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ended_at_type_0 = datetime.datetime.fromisoformat(data)

                return ended_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        ended_at = _parse_ended_at(d.pop("endedAt", UNSET))

        def _parse_duration_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        duration_seconds = _parse_duration_seconds(d.pop("durationSeconds", UNSET))

        _status = d.pop("status", UNSET)
        status: FocusSessionStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = FocusSessionStatus(_status)

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        focus_session = cls(
            id=id,
            user=user,
            task=task,
            title=title,
            started_at=started_at,
            ended_at=ended_at,
            duration_seconds=duration_seconds,
            status=status,
            note=note,
        )

        focus_session.additional_properties = d
        return focus_session

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
