from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="BatchesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class BatchesUnarchive:
    """The request body for unarchiving Batches."""

    _batch_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("batch_ids={}".format(repr(self._batch_ids)))
        return "BatchesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_ids = self._batch_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "batchIds": batch_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_ids = cast(List[str], d.pop("batchIds"))

        batches_unarchive = cls(
            batch_ids=batch_ids,
        )

        return batches_unarchive

    @property
    def batch_ids(self) -> List[str]:
        return self._batch_ids

    @batch_ids.setter
    def batch_ids(self, value: List[str]) -> None:
        self._batch_ids = value
