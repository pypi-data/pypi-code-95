from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.assay_run import AssayRun

T = TypeVar("T", bound="AssayRunsBulkGet")


@attr.s(auto_attribs=True, repr=False)
class AssayRunsBulkGet:
    """  """

    _assay_runs: List[AssayRun]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_runs={}".format(repr(self._assay_runs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunsBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_runs = []
        for assay_runs_item_data in self._assay_runs:
            assay_runs_item = assay_runs_item_data.to_dict()

            assay_runs.append(assay_runs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assayRuns": assay_runs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_runs = []
        _assay_runs = d.pop("assayRuns")
        for assay_runs_item_data in _assay_runs:
            assay_runs_item = AssayRun.from_dict(assay_runs_item_data)

            assay_runs.append(assay_runs_item)

        assay_runs_bulk_get = cls(
            assay_runs=assay_runs,
        )

        assay_runs_bulk_get.additional_properties = d
        return assay_runs_bulk_get

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
    def assay_runs(self) -> List[AssayRun]:
        return self._assay_runs

    @assay_runs.setter
    def assay_runs(self, value: List[AssayRun]) -> None:
        self._assay_runs = value
