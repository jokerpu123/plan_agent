from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statistics_result_daily import StatisticsResultDaily
    from ..models.statistics_result_priority_counts import (
        StatisticsResultPriorityCounts,
    )
    from ..models.statistics_result_status_counts import StatisticsResultStatusCounts


T = TypeVar("T", bound="StatisticsResult")


@_attrs_define
class StatisticsResult:
    """
    Attributes:
        from_ (datetime.date | Unset):
        to (datetime.date | Unset):
        total_tasks (int | Unset):
        completed_tasks (int | Unset):
        completion_rate (float | Unset):
        overdue_tasks (int | Unset):
        estimated_minutes (int | Unset):
        actual_minutes (int | Unset):
        focus_minutes (int | Unset):
        focus_sessions (int | Unset):
        status_counts (StatisticsResultStatusCounts | Unset):
        priority_counts (StatisticsResultPriorityCounts | Unset):
        daily (StatisticsResultDaily | Unset):
    """

    from_: datetime.date | Unset = UNSET
    to: datetime.date | Unset = UNSET
    total_tasks: int | Unset = UNSET
    completed_tasks: int | Unset = UNSET
    completion_rate: float | Unset = UNSET
    overdue_tasks: int | Unset = UNSET
    estimated_minutes: int | Unset = UNSET
    actual_minutes: int | Unset = UNSET
    focus_minutes: int | Unset = UNSET
    focus_sessions: int | Unset = UNSET
    status_counts: StatisticsResultStatusCounts | Unset = UNSET
    priority_counts: StatisticsResultPriorityCounts | Unset = UNSET
    daily: StatisticsResultDaily | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_: str | Unset = UNSET
        if not isinstance(self.from_, Unset):
            from_ = self.from_.isoformat()

        to: str | Unset = UNSET
        if not isinstance(self.to, Unset):
            to = self.to.isoformat()

        total_tasks = self.total_tasks

        completed_tasks = self.completed_tasks

        completion_rate = self.completion_rate

        overdue_tasks = self.overdue_tasks

        estimated_minutes = self.estimated_minutes

        actual_minutes = self.actual_minutes

        focus_minutes = self.focus_minutes

        focus_sessions = self.focus_sessions

        status_counts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.status_counts, Unset):
            status_counts = self.status_counts.to_dict()

        priority_counts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.priority_counts, Unset):
            priority_counts = self.priority_counts.to_dict()

        daily: dict[str, Any] | Unset = UNSET
        if not isinstance(self.daily, Unset):
            daily = self.daily.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to
        if total_tasks is not UNSET:
            field_dict["totalTasks"] = total_tasks
        if completed_tasks is not UNSET:
            field_dict["completedTasks"] = completed_tasks
        if completion_rate is not UNSET:
            field_dict["completionRate"] = completion_rate
        if overdue_tasks is not UNSET:
            field_dict["overdueTasks"] = overdue_tasks
        if estimated_minutes is not UNSET:
            field_dict["estimatedMinutes"] = estimated_minutes
        if actual_minutes is not UNSET:
            field_dict["actualMinutes"] = actual_minutes
        if focus_minutes is not UNSET:
            field_dict["focusMinutes"] = focus_minutes
        if focus_sessions is not UNSET:
            field_dict["focusSessions"] = focus_sessions
        if status_counts is not UNSET:
            field_dict["statusCounts"] = status_counts
        if priority_counts is not UNSET:
            field_dict["priorityCounts"] = priority_counts
        if daily is not UNSET:
            field_dict["daily"] = daily

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.statistics_result_daily import (
            StatisticsResultDaily,
        )
        from ..models.statistics_result_priority_counts import (
            StatisticsResultPriorityCounts,
        )
        from ..models.statistics_result_status_counts import (
            StatisticsResultStatusCounts,
        )

        d = dict(src_dict)
        _from_ = d.pop("from", UNSET)
        from_: datetime.date | Unset
        if isinstance(_from_, Unset):
            from_ = UNSET
        else:
            from_ = datetime.date.fromisoformat(_from_)

        _to = d.pop("to", UNSET)
        to: datetime.date | Unset
        if isinstance(_to, Unset):
            to = UNSET
        else:
            to = datetime.date.fromisoformat(_to)

        total_tasks = d.pop("totalTasks", UNSET)

        completed_tasks = d.pop("completedTasks", UNSET)

        completion_rate = d.pop("completionRate", UNSET)

        overdue_tasks = d.pop("overdueTasks", UNSET)

        estimated_minutes = d.pop("estimatedMinutes", UNSET)

        actual_minutes = d.pop("actualMinutes", UNSET)

        focus_minutes = d.pop("focusMinutes", UNSET)

        focus_sessions = d.pop("focusSessions", UNSET)

        _status_counts = d.pop("statusCounts", UNSET)
        status_counts: StatisticsResultStatusCounts | Unset
        if isinstance(_status_counts, Unset):
            status_counts = UNSET
        else:
            status_counts = StatisticsResultStatusCounts.from_dict(_status_counts)

        _priority_counts = d.pop("priorityCounts", UNSET)
        priority_counts: StatisticsResultPriorityCounts | Unset
        if isinstance(_priority_counts, Unset):
            priority_counts = UNSET
        else:
            priority_counts = StatisticsResultPriorityCounts.from_dict(_priority_counts)

        _daily = d.pop("daily", UNSET)
        daily: StatisticsResultDaily | Unset
        if isinstance(_daily, Unset):
            daily = UNSET
        else:
            daily = StatisticsResultDaily.from_dict(_daily)

        statistics_result = cls(
            from_=from_,
            to=to,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            overdue_tasks=overdue_tasks,
            estimated_minutes=estimated_minutes,
            actual_minutes=actual_minutes,
            focus_minutes=focus_minutes,
            focus_sessions=focus_sessions,
            status_counts=status_counts,
            priority_counts=priority_counts,
            daily=daily,
        )

        statistics_result.additional_properties = d
        return statistics_result

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
