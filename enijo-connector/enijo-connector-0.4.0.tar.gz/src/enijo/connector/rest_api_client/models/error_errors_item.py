from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ErrorErrorsItem")


@attr.s(auto_attribs=True)
class ErrorErrorsItem:
    """  """

    field: Union[Unset, str] = UNSET
    messages: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field = self.field
        messages: Union[Unset, List[str]] = UNSET
        if not isinstance(self.messages, Unset):
            messages = self.messages

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field is not UNSET:
            field_dict["field"] = field
        if messages is not UNSET:
            field_dict["messages"] = messages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        field = d.pop("field", UNSET)

        messages = cast(List[str], d.pop("messages", UNSET))

        error_errors_item = cls(
            field=field,
            messages=messages,
        )

        error_errors_item.additional_properties = d
        return error_errors_item

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
