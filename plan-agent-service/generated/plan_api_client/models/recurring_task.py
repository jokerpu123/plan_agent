from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.recurring_task_priority import RecurringTaskPriority
from ..models.recurring_task_reminder_channel import RecurringTaskReminderChannel
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="RecurringTask")


@_attrs_define
class RecurringTask:
    """
    Attributes:
        id (int | Unset):
        content (str | Unset):
        start_date (datetime.date | Unset):
        end_date (datetime.date | None | Unset):
        weekdays (str | Unset):
        active (bool | Unset):
        priority (RecurringTaskPriority | Unset):
        start_time (None | str | Unset):  Example: 09:00:00.
        end_time (None | str | Unset):  Example: 10:00:00.
        estimated_minutes (int | None | Unset):
        reminder_enabled (bool | Unset):
        reminder_channel (RecurringTaskReminderChannel | Unset): 提醒渠道；历史数据可能为空
        reminder_minutes_before (int | None | Unset):
        user (User | Unset):
    """

    id: int | Unset = UNSET
    content: str | Unset = UNSET
    start_date: datetime.date | Unset = UNSET
    end_date: datetime.date | None | Unset = UNSET
    weekdays: str | Unset = UNSET
    active: bool | Unset = UNSET
    priority: RecurringTaskPriority | Unset = UNSET
    start_time: None | str | Unset = UNSET
    end_time: None | str | Unset = UNSET
    estimated_minutes: int | None | Unset = UNSET
    reminder_enabled: bool | Unset = UNSET
    reminder_channel: RecurringTaskReminderChannel | Unset = UNSET
    reminder_minutes_before: int | None | Unset = UNSET
    user: User | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        content = self.content

        start_date: str | Unset = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: None | str | Unset
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.date):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        weekdays = self.weekdays

        active = self.active

        priority: str | Unset = UNSET
        if not isinstance(self.priority, Unset):
            priority = self.priority.value

        start_time: None | str | Unset
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time

        end_time: None | str | Unset
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        else:
            end_time = self.end_time

        estimated_minutes: int | None | Unset
        if isinstance(self.estimated_minutes, Unset):
            estimated_minutes = UNSET
        else:
            estimated_minutes = self.estimated_minutes

        reminder_enabled = self.reminder_enabled

        reminder_channel: str | Unset = UNSET
        if not isinstance(self.reminder_channel, Unset):
            reminder_channel = self.reminder_channel.value

        reminder_minutes_before: int | None | Unset
        if isinstance(self.reminder_minutes_before, Unset):
            reminder_minutes_before = UNSET
        else:
            reminder_minutes_before = self.reminder_minutes_before

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if content is not UNSET:
            field_dict["content"] = content
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if weekdays is not UNSET:
            field_dict["weekdays"] = weekdays
        if active is not UNSET:
            field_dict["active"] = active
        if priority is not UNSET:
            field_dict["priority"] = priority
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if estimated_minutes is not UNSET:
            field_dict["estimatedMinutes"] = estimated_minutes
        if reminder_enabled is not UNSET:
            field_dict["reminderEnabled"] = reminder_enabled
        if reminder_channel is not UNSET:
            field_dict["reminderChannel"] = reminder_channel
        if reminder_minutes_before is not UNSET:
            field_dict["reminderMinutesBefore"] = reminder_minutes_before
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user import User

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        content = d.pop("content", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: datetime.date | Unset
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = datetime.date.fromisoformat(_start_date)

        def _parse_end_date(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = datetime.date.fromisoformat(data)

                return end_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        end_date = _parse_end_date(d.pop("endDate", UNSET))

        weekdays = d.pop("weekdays", UNSET)

        active = d.pop("active", UNSET)

        _priority = d.pop("priority", UNSET)
        priority: RecurringTaskPriority | Unset
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = RecurringTaskPriority(_priority)

        def _parse_start_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        start_time = _parse_start_time(d.pop("startTime", UNSET))

        def _parse_end_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end_time = _parse_end_time(d.pop("endTime", UNSET))

        def _parse_estimated_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        estimated_minutes = _parse_estimated_minutes(d.pop("estimatedMinutes", UNSET))

        reminder_enabled = d.pop("reminderEnabled", UNSET)

        _reminder_channel = d.pop("reminderChannel", UNSET)
        reminder_channel: RecurringTaskReminderChannel | Unset
        if isinstance(_reminder_channel, Unset):
            reminder_channel = UNSET
        else:
            reminder_channel = RecurringTaskReminderChannel(_reminder_channel)

        def _parse_reminder_minutes_before(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        reminder_minutes_before = _parse_reminder_minutes_before(
            d.pop("reminderMinutesBefore", UNSET)
        )

        _user = d.pop("user", UNSET)
        user: User | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = User.from_dict(_user)

        recurring_task = cls(
            id=id,
            content=content,
            start_date=start_date,
            end_date=end_date,
            weekdays=weekdays,
            active=active,
            priority=priority,
            start_time=start_time,
            end_time=end_time,
            estimated_minutes=estimated_minutes,
            reminder_enabled=reminder_enabled,
            reminder_channel=reminder_channel,
            reminder_minutes_before=reminder_minutes_before,
            user=user,
        )

        recurring_task.additional_properties = d
        return recurring_task

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
