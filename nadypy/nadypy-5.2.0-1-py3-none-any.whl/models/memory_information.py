from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="MemoryInformation")


@attr.s(auto_attribs=True)
class MemoryInformation:
    """ """

    current_usage: Union[Unset, int] = UNSET
    current_usage_real: Union[Unset, int] = UNSET
    peak_usage: Union[Unset, int] = UNSET
    peak_usage_real: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        current_usage = self.current_usage
        current_usage_real = self.current_usage_real
        peak_usage = self.peak_usage
        peak_usage_real = self.peak_usage_real

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if current_usage is not UNSET:
            field_dict["current_usage"] = current_usage
        if current_usage_real is not UNSET:
            field_dict["current_usage_real"] = current_usage_real
        if peak_usage is not UNSET:
            field_dict["peak_usage"] = peak_usage
        if peak_usage_real is not UNSET:
            field_dict["peak_usage_real"] = peak_usage_real

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        current_usage = d.pop("current_usage", UNSET)

        current_usage_real = d.pop("current_usage_real", UNSET)

        peak_usage = d.pop("peak_usage", UNSET)

        peak_usage_real = d.pop("peak_usage_real", UNSET)

        memory_information = cls(
            current_usage=current_usage,
            current_usage_real=current_usage_real,
            peak_usage=peak_usage,
            peak_usage_real=peak_usage_real,
        )

        memory_information.additional_properties = d
        return memory_information

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
