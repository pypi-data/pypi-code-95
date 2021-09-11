from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.assay_result import AssayResult

T = TypeVar("T", bound="AssayResultsBulkGet")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsBulkGet:
    """  """

    _assay_results: List[AssayResult]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultsBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results = []
        for assay_results_item_data in self._assay_results:
            assay_results_item = assay_results_item_data.to_dict()

            assay_results.append(assay_results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assayResults": assay_results,
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

        assay_results_bulk_get = cls(
            assay_results=assay_results,
        )

        assay_results_bulk_get.additional_properties = d
        return assay_results_bulk_get

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
