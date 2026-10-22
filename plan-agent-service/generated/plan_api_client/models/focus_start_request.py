from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="FocusStartRequest")


@_attrs_define
class FocusStartRequest:
    """
    Attributes:
        user_id (int | Unset):
        task_id (int | Unset):
        title (str | Unset):
    """

    user_id: int | Unset = UNSET
    task_id: int | Unset = UNSET
    title: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        task_id = self.task_id

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if task_id is not UNSET:
            field_dict["taskId"] = task_id
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        user_id = d.pop("userId", UNSET)

        task_id = d.pop("taskId", UNSET)

        title = d.pop("title", UNSET)

        focus_start_request = cls(
            user_id=user_id,
            task_id=task_id,
            title=title,
        )

        focus_start_request.additional_properties = d
        return focus_start_request

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
