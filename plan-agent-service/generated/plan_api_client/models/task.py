from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..models.task_priority import TaskPriority
from ..models.task_reminder_channel import TaskReminderChannel
from ..models.task_status import TaskStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subtask import Subtask
    from ..models.user import User


T = TypeVar("T", bound="Task")


@_attrs_define
class Task:
    """
    Attributes:
        id (int | Unset):
        content (str | Unset):
        task_date (datetime.date | Unset):
        completed (bool | Unset):
        status (TaskStatus | Unset):
        priority (TaskPriority | Unset):
        start_time (None | str | Unset):  Example: 09:00:00.
        end_time (None | str | Unset):  Example: 10:00:00.
        deadline (datetime.datetime | None | Unset):
        estimated_minutes (int | None | Unset):
        actual_minutes (int | None | Unset):
        completed_at (datetime.datetime | None | Unset):
        reminder_enabled (bool | Unset):
        reminder_channel (TaskReminderChannel | Unset): 提醒渠道；历史数据可能为空
        reminder_minutes_before (int | None | Unset):
        reminder_sent (bool | Unset):
        plan_type (str | Unset):
        user (User | Unset):
        subtasks (list[Subtask] | Unset):
    """

    id: int | Unset = UNSET
    content: str | Unset = UNSET
    task_date: datetime.date | Unset = UNSET
    completed: bool | Unset = UNSET
    status: TaskStatus | Unset = UNSET
    priority: TaskPriority | Unset = UNSET
    start_time: None | str | Unset = UNSET
    end_time: None | str | Unset = UNSET
    deadline: datetime.datetime | None | Unset = UNSET
    estimated_minutes: int | None | Unset = UNSET
    actual_minutes: int | None | Unset = UNSET
    completed_at: datetime.datetime | None | Unset = UNSET
    reminder_enabled: bool | Unset = UNSET
    reminder_channel: TaskReminderChannel | Unset = UNSET
    reminder_minutes_before: int | None | Unset = UNSET
    reminder_sent: bool | Unset = UNSET
    plan_type: str | Unset = UNSET
    user: User | Unset = UNSET
    subtasks: list[Subtask] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        content = self.content

        task_date: str | Unset = UNSET
        if not isinstance(self.task_date, Unset):
            task_date = self.task_date.isoformat()

        completed = self.completed

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

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

        deadline: None | str | Unset
        if isinstance(self.deadline, Unset):
            deadline = UNSET
        elif isinstance(self.deadline, datetime.datetime):
            deadline = self.deadline.isoformat()
        else:
            deadline = self.deadline

        estimated_minutes: int | None | Unset
        if isinstance(self.estimated_minutes, Unset):
            estimated_minutes = UNSET
        else:
            estimated_minutes = self.estimated_minutes

        actual_minutes: int | None | Unset
        if isinstance(self.actual_minutes, Unset):
            actual_minutes = UNSET
        else:
            actual_minutes = self.actual_minutes

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        reminder_enabled = self.reminder_enabled

        reminder_channel: str | Unset = UNSET
        if not isinstance(self.reminder_channel, Unset):
            reminder_channel = self.reminder_channel.value

        reminder_minutes_before: int | None | Unset
        if isinstance(self.reminder_minutes_before, Unset):
            reminder_minutes_before = UNSET
        else:
            reminder_minutes_before = self.reminder_minutes_before

        reminder_sent = self.reminder_sent

        plan_type = self.plan_type

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        subtasks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.subtasks, Unset):
            subtasks = []
            for subtasks_item_data in self.subtasks:
                subtasks_item = subtasks_item_data.to_dict()
                subtasks.append(subtasks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if content is not UNSET:
            field_dict["content"] = content
        if task_date is not UNSET:
            field_dict["taskDate"] = task_date
        if completed is not UNSET:
            field_dict["completed"] = completed
        if status is not UNSET:
            field_dict["status"] = status
        if priority is not UNSET:
            field_dict["priority"] = priority
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if deadline is not UNSET:
            field_dict["deadline"] = deadline
        if estimated_minutes is not UNSET:
            field_dict["estimatedMinutes"] = estimated_minutes
        if actual_minutes is not UNSET:
            field_dict["actualMinutes"] = actual_minutes
        if completed_at is not UNSET:
            field_dict["completedAt"] = completed_at
        if reminder_enabled is not UNSET:
            field_dict["reminderEnabled"] = reminder_enabled
        if reminder_channel is not UNSET:
            field_dict["reminderChannel"] = reminder_channel
        if reminder_minutes_before is not UNSET:
            field_dict["reminderMinutesBefore"] = reminder_minutes_before
        if reminder_sent is not UNSET:
            field_dict["reminderSent"] = reminder_sent
        if plan_type is not UNSET:
            field_dict["planType"] = plan_type
        if user is not UNSET:
            field_dict["user"] = user
        if subtasks is not UNSET:
            field_dict["subtasks"] = subtasks

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.subtask import Subtask
        from ..models.user import User

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        content = d.pop("content", UNSET)

        _task_date = d.pop("taskDate", UNSET)
        task_date: datetime.date | Unset
        if isinstance(_task_date, Unset):
            task_date = UNSET
        else:
            task_date = datetime.date.fromisoformat(_task_date)

        completed = d.pop("completed", UNSET)

        _status = d.pop("status", UNSET)
        status: TaskStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = TaskStatus(_status)

        _priority = d.pop("priority", UNSET)
        priority: TaskPriority | Unset
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = TaskPriority(_priority)

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

        def _parse_deadline(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deadline_type_0 = datetime.datetime.fromisoformat(data)

                return deadline_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        deadline = _parse_deadline(d.pop("deadline", UNSET))

        def _parse_estimated_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        estimated_minutes = _parse_estimated_minutes(d.pop("estimatedMinutes", UNSET))

        def _parse_actual_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        actual_minutes = _parse_actual_minutes(d.pop("actualMinutes", UNSET))

        def _parse_completed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = datetime.datetime.fromisoformat(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_at = _parse_completed_at(d.pop("completedAt", UNSET))

        reminder_enabled = d.pop("reminderEnabled", UNSET)

        _reminder_channel = d.pop("reminderChannel", UNSET)
        reminder_channel: TaskReminderChannel | Unset
        if isinstance(_reminder_channel, Unset):
            reminder_channel = UNSET
        else:
            reminder_channel = TaskReminderChannel(_reminder_channel)

        def _parse_reminder_minutes_before(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        reminder_minutes_before = _parse_reminder_minutes_before(
            d.pop("reminderMinutesBefore", UNSET)
        )

        reminder_sent = d.pop("reminderSent", UNSET)

        plan_type = d.pop("planType", UNSET)

        _user = d.pop("user", UNSET)
        user: User | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = User.from_dict(_user)

        _subtasks = d.pop("subtasks", UNSET)
        subtasks: list[Subtask] | Unset = UNSET
        if _subtasks is not UNSET:
            subtasks = []
            for subtasks_item_data in _subtasks:
                subtasks_item = Subtask.from_dict(subtasks_item_data)

                subtasks.append(subtasks_item)

        task = cls(
            id=id,
            content=content,
            task_date=task_date,
            completed=completed,
            status=status,
            priority=priority,
            start_time=start_time,
            end_time=end_time,
            deadline=deadline,
            estimated_minutes=estimated_minutes,
            actual_minutes=actual_minutes,
            completed_at=completed_at,
            reminder_enabled=reminder_enabled,
            reminder_channel=reminder_channel,
            reminder_minutes_before=reminder_minutes_before,
            reminder_sent=reminder_sent,
            plan_type=plan_type,
            user=user,
            subtasks=subtasks,
        )

        task.additional_properties = d
        return task

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
