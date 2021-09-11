from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.assay_result import AssayResult

T = TypeVar("T", bound="AssayResultsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsPaginatedList:
    """  """

    _assay_results: List[AssayResult]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results = []
        for assay_results_item_data in self._assay_results:
            assay_results_item = assay_results_item_data.to_dict()

            assay_results.append(assay_results_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assayResults": assay_results,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_results = []
        _assay_results = d.pop("assayResults")
        for assay_results_item_data in _assay_results:
            assay_results_item = AssayResult.from_dict(assay_results_item_data)

            assay_results.append(assay_results_item)

        next_token = d.pop("nextToken")

        assay_results_paginated_list = cls(
            assay_results=assay_results,
            next_token=next_token,
        )

        assay_results_paginated_list.additional_properties = d
        return assay_results_paginated_list

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
    def assay_results(self) -> List[AssayResult]:
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[AssayResult]) -> None:
        self._assay_results = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
