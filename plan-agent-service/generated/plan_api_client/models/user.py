from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (int | Unset):
        email (str | Unset):
        phone (None | str | Unset):
        daily_capacity_minutes (int | None | Unset):
        minimum_break_minutes (int | None | Unset):
    """

    id: int | Unset = UNSET
    email: str | Unset = UNSET
    phone: None | str | Unset = UNSET
    daily_capacity_minutes: int | None | Unset = UNSET
    minimum_break_minutes: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        phone: None | str | Unset
        if isinstance(self.phone, Unset):
            phone = UNSET
        else:
            phone = self.phone

        daily_capacity_minutes: int | None | Unset
        if isinstance(self.daily_capacity_minutes, Unset):
            daily_capacity_minutes = UNSET
        else:
            daily_capacity_minutes = self.daily_capacity_minutes

        minimum_break_minutes: int | None | Unset
        if isinstance(self.minimum_break_minutes, Unset):
            minimum_break_minutes = UNSET
        else:
            minimum_break_minutes = self.minimum_break_minutes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if email is not UNSET:
            field_dict["email"] = email
        if phone is not UNSET:
            field_dict["phone"] = phone
        if daily_capacity_minutes is not UNSET:
            field_dict["dailyCapacityMinutes"] = daily_capacity_minutes
        if minimum_break_minutes is not UNSET:
            field_dict["minimumBreakMinutes"] = minimum_break_minutes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        email = d.pop("email", UNSET)

        def _parse_phone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone = _parse_phone(d.pop("phone", UNSET))

        def _parse_daily_capacity_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        daily_capacity_minutes = _parse_daily_capacity_minutes(
            d.pop("dailyCapacityMinutes", UNSET)
        )

        def _parse_minimum_break_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        minimum_break_minutes = _parse_minimum_break_minutes(
            d.pop("minimumBreakMinutes", UNSET)
        )

        user = cls(
            id=id,
            email=email,
            phone=phone,
            daily_capacity_minutes=daily_capacity_minutes,
            minimum_break_minutes=minimum_break_minutes,
        )

        user.additional_properties = d
        return user

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
