from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.assay_result_create import AssayResultCreate

T = TypeVar("T", bound="AssayResultsBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsBulkCreateRequest:
    """  """

    _assay_results: List[AssayResultCreate]

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        return "AssayResultsBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results = []
        for assay_results_item_data in self._assay_results:
            assay_results_item = assay_results_item_data.to_dict()

            assay_results.append(assay_results_item)

        field_dict: Dict[str, Any] = {}
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
            assay_results_item = AssayResultCreate.from_dict(assay_results_item_data)

            assay_results.append(assay_results_item)

        assay_results_bulk_create_request = cls(
            assay_results=assay_results,
        )

        return assay_results_bulk_create_request

    @property
    def assay_results(self) -> List[AssayResultCreate]:
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[AssayResultCreate]) -> None:
        self._assay_results = value
