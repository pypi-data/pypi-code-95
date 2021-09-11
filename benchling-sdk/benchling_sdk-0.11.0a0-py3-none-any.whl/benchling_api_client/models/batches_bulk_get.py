from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.batch import Batch

T = TypeVar("T", bound="BatchesBulkGet")


@attr.s(auto_attribs=True, repr=False)
class BatchesBulkGet:
    """  """

    _batches: List[Batch]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batches={}".format(repr(self._batches)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BatchesBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batches = []
        for batches_item_data in self._batches:
            batches_item = batches_item_data.to_dict()

            batches.append(batches_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batches": batches,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batches = []
        _batches = d.pop("batches")
        for batches_item_data in _batches:
            batches_item = Batch.from_dict(batches_item_data)

            batches.append(batches_item)

        batches_bulk_get = cls(
            batches=batches,
        )

        batches_bulk_get.additional_properties = d
        return batches_bulk_get

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
    def batches(self) -> List[Batch]:
        return self._batches

    @batches.setter
    def batches(self, value: List[Batch]) -> None:
        self._batches = value
