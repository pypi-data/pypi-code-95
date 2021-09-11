from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.dropdown_summary import DropdownSummary

T = TypeVar("T", bound="DropdownSummariesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DropdownSummariesPaginatedList:
    """  """

    _dropdowns: List[DropdownSummary]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dropdowns={}".format(repr(self._dropdowns)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DropdownSummariesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdowns = []
        for dropdowns_item_data in self._dropdowns:
            dropdowns_item = dropdowns_item_data.to_dict()

            dropdowns.append(dropdowns_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dropdowns": dropdowns,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dropdowns = []
        _dropdowns = d.pop("dropdowns")
        for dropdowns_item_data in _dropdowns:
            dropdowns_item = DropdownSummary.from_dict(dropdowns_item_data)

            dropdowns.append(dropdowns_item)

        next_token = d.pop("nextToken")

        dropdown_summaries_paginated_list = cls(
            dropdowns=dropdowns,
            next_token=next_token,
        )

        dropdown_summaries_paginated_list.additional_properties = d
        return dropdown_summaries_paginated_list

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def dropdowns(self) -> List[DropdownSummary]:
        return self._dropdowns

    @dropdowns.setter
    def dropdowns(self, value: List[DropdownSummary]) -> None:
        self._dropdowns = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
