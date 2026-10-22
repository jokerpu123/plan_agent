from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskAnalysisResult")


@_attrs_define
class TaskAnalysisResult:
    """
    Attributes:
        reasonable (bool | Unset):
        planned_minutes (int | Unset):
        capacity_minutes (int | Unset):
        remaining_minutes (int | Unset):
        warnings (list[str] | Unset):
    """

    reasonable: bool | Unset = UNSET
    planned_minutes: int | Unset = UNSET
    capacity_minutes: int | Unset = UNSET
    remaining_minutes: int | Unset = UNSET
    warnings: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reasonable = self.reasonable

        planned_minutes = self.planned_minutes

        capacity_minutes = self.capacity_minutes

        remaining_minutes = self.remaining_minutes

        warnings: list[str] | Unset = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = self.warnings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reasonable is not UNSET:
            field_dict["reasonable"] = reasonable
        if planned_minutes is not UNSET:
            field_dict["plannedMinutes"] = planned_minutes
        if capacity_minutes is not UNSET:
            field_dict["capacityMinutes"] = capacity_minutes
        if remaining_minutes is not UNSET:
            field_dict["remainingMinutes"] = remaining_minutes
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        reasonable = d.pop("reasonable", UNSET)

        planned_minutes = d.pop("plannedMinutes", UNSET)

        capacity_minutes = d.pop("capacityMinutes", UNSET)

        remaining_minutes = d.pop("remainingMinutes", UNSET)

        warnings = cast(list[str], d.pop("warnings", UNSET))

        task_analysis_result = cls(
            reasonable=reasonable,
            planned_minutes=planned_minutes,
            capacity_minutes=capacity_minutes,
            remaining_minutes=remaining_minutes,
            warnings=warnings,
        )

        task_analysis_result.additional_properties = d
        return task_analysis_result

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
